from rest_framework import serializers
from .models import Category, Subcategory, Product, ProductVariant, ProductImage, Order, OrderItem, ContactMessage


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'description', 'category', 'created_at']


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'subcategories', 'product_count', 'created_at']


class ProductImageSerializer(serializers.ModelSerializer):
    # Koristimo SerializerMethodField za read, ali dozvoljavamo write preko image field-a
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        # Vrati URL slike - može biti Cloudinary ili lokalni /media/
        if obj.image and obj.image.name:
            try:
                url = obj.image.url
                # Ako je URL potpuna adresa (http/https), vrati ga direktno (Cloudinary)
                if url.startswith('http://') or url.startswith('https://'):
                    return url
                # Inače je lokalni URL, vrati ga direktno
                return url
            except (ValueError, AttributeError):
                return None
        return None
    
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'image_url', 'alt_text', 'is_primary', 'order', 'created_at']
        extra_kwargs = {
            'image': {'write_only': True}  # image je samo za write
        }
    
    def to_representation(self, instance):
        # Override to_representation da vratimo image_url kao image
        ret = super().to_representation(instance)
        # Zameni image_url sa image za kompatibilnost sa frontend-om
        if 'image_url' in ret:
            ret['image'] = ret.pop('image_url')
        return ret


class ProductVariantSerializer(serializers.ModelSerializer):
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    effective_length_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'name', 'price', 'on_sale', 'sale_price',
            'current_price', 'final_price', 'sku',
            'in_stock', 'stock_quantity', 'length_per_unit', 'effective_length_per_unit',
            'created_at'
        ]
        extra_kwargs = {
            'length_per_unit': {'required': False, 'allow_null': True}
        }


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    has_sale_variants = serializers.BooleanField(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'on_sale', 'sale_price',
            'category', 'category_name', 'subcategory', 'subcategory_name',
            'current_price', 'min_price', 'has_sale_variants',
            'featured', 'in_stock', 'stock_quantity', 'sold_by_length', 'length_per_unit',
            'variants', 'images', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'length_per_unit': {'required': False}
        }
    
    def validate_length_per_unit(self, value):
        """Validacija za length_per_unit"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Dužina mora biti veća od 0")
        return value
    
    def create(self, validated_data):
        """Override create da osigura da length_per_unit ima default vrednost"""
        if 'length_per_unit' not in validated_data or validated_data.get('length_per_unit') is None:
            validated_data['length_per_unit'] = 6.0
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Override update da osigura da length_per_unit ima default vrednost"""
        if 'length_per_unit' not in validated_data or validated_data.get('length_per_unit') is None:
            # Ako instance već ima length_per_unit, zadrži ga, inače koristi default
            if hasattr(instance, 'length_per_unit') and instance.length_per_unit is not None:
                validated_data['length_per_unit'] = instance.length_per_unit
            else:
                validated_data['length_per_unit'] = 6.0
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        """Override to_representation da osigura da length_per_unit uvek ima vrednost"""
        data = super().to_representation(instance)
        # Osiguraj da length_per_unit uvek ima vrednost
        if 'length_per_unit' not in data or data['length_per_unit'] is None:
            data['length_per_unit'] = str(6.0)
        # Konvertuj Decimal u string za JSON serializaciju
        if 'length_per_unit' in data and isinstance(data['length_per_unit'], (int, float)):
            data['length_per_unit'] = str(float(data['length_per_unit']))
        return data


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True, allow_null=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True, allow_null=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    sold_by_length = serializers.SerializerMethodField()
    effective_length_per_unit = serializers.SerializerMethodField()

    def get_sold_by_length(self, obj):
        """Vraća da li je proizvod prodavan po metraži"""
        if obj.product:
            return obj.product.sold_by_length
        return False

    def get_effective_length_per_unit(self, obj):
        """Vraća efektivnu dužinu po jedinici (iz varijante ili proizvoda)"""
        if obj.variant and obj.variant.effective_length_per_unit:
            return obj.variant.effective_length_per_unit
        if obj.product and obj.product.length_per_unit:
            return obj.product.length_per_unit
        return None

    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'product', 'product_name', 'variant', 'variant_name',
            'quantity', 'unit_price', 'total_price', 'sold_by_length', 'effective_length_per_unit'
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'customer_phone', 'customer_email',
            'address', 'city', 'notes', 'status', 'total_amount',
            'items', 'created_at', 'updated_at'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )

    # Lista gradova u Republici Srbiji
    SERBIAN_CITIES = [
        'Beograd', 'Novi Sad', 'Niš', 'Kragujevac', 'Subotica', 'Zrenjanin', 'Pančevo',
        'Čačak', 'Novi Pazar', 'Kraljevo', 'Smederevo', 'Leskovac', 'Valjevo', 'Kruševac',
        'Vranje', 'Šabac', 'Užice', 'Sombor', 'Požarevac', 'Pirot', 'Zaječar', 'Kikinda',
        'Sremska Mitrovica', 'Jagodina', 'Vršac', 'Bor', 'Prokuplje', 'Loznica', 'Smederevska Palanka',
        'Inđija', 'Vrbas', 'Ruma', 'Bačka Palanka', 'Stara Pazova', 'Kovin', 'Aranđelovac',
        'Obrenovac', 'Lazarevac', 'Mladenovac', 'Batajnica', 'Surčin', 'Barajevo', 'Grocka',
        'Palilula', 'Zvezdara', 'Voždovac', 'Savski Venac', 'Stari Grad', 'Vračar', 'Novi Beograd',
        'Zemun', 'Surčin', 'Čukarica', 'Rakovica', 'Sopot', 'Gradska opština', 'Opština'
    ]

    class Meta:
        model = Order
        fields = [
            'customer_name', 'customer_phone', 'customer_email',
            'address', 'city', 'notes', 'items'
        ]
        extra_kwargs = {
            'customer_name': {'required': True},
            'customer_phone': {'required': True},
            'customer_email': {'allow_null': True, 'allow_blank': True, 'required': False},
            'address': {'required': True},
            'city': {'required': True},
            'notes': {'allow_null': True, 'allow_blank': True, 'required': False},
        }
    
    def validate_city(self, value):
        """Validacija da je grad u Republici Srbiji"""
        if not value or not value.strip():
            raise serializers.ValidationError("Grad je obavezan")
        
        city_normalized = value.strip().title()
        
        # Proveri da li je grad u listi (case-insensitive)
        if city_normalized not in [c.title() for c in self.SERBIAN_CITIES]:
            # Dozvoli i druge gradove ako su validni (može biti manji grad)
            # Ali proveri da nije očigledno van Srbije
            invalid_cities = ['Zagreb', 'Ljubljana', 'Sarajevo', 'Podgorica', 'Skopje', 'Tirana', 'Sofia', 'Bucharest', 'Budapest']
            if city_normalized in invalid_cities:
                raise serializers.ValidationError("Dostava je moguća samo na teritoriji Republike Srbije")
        
        return city_normalized
    
    def validate(self, data):
        # Konvertuj prazne stringove u None za opciona polja
        if 'customer_email' in data and data['customer_email'] == '':
            data['customer_email'] = None
        if 'notes' in data and data['notes'] == '':
            data['notes'] = None
        if 'address' in data:
            data['address'] = data['address'].strip()
        if 'city' in data:
            data['city'] = data['city'].strip()
        return data
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # First calculate total_amount
        total_amount = 0
        items_to_create = []
        
        for item_data in items_data:
            product_id = item_data.get('product') or item_data.get('product_id')
            variant_id = item_data.get('variant') or item_data.get('variant_id')
            # Convert quantity to Decimal to support decimal quantities for products sold by length
            from decimal import Decimal
            quantity = Decimal(str(item_data.get('quantity', 1)))
            
            # Get product and variant
            product = None
            variant = None
            
            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    pass
            
            if variant_id:
                try:
                    variant = ProductVariant.objects.get(id=variant_id)
                except ProductVariant.DoesNotExist:
                    pass
            
            # Calculate price
            if variant:
                unit_price = variant.final_price
                # Ako product nije postavljen, uzmi ga iz variant.product
                if not product and hasattr(variant, 'product') and variant.product:
                    product = variant.product
                product_name = product.name if product else (variant.product.name if hasattr(variant, 'product') and variant.product else 'Unknown Product')
                variant_name = variant.name
            elif product:
                unit_price = product.current_price
                product_name = product.name
                variant_name = ''
            else:
                # Fallback - use price from item_data if available
                unit_price = item_data.get('unit_price', 0)
                product_name = item_data.get('product_name', 'Unknown Product')
                variant_name = item_data.get('variant_name', '')
            
            total_price = unit_price * quantity
            total_amount += total_price
            
            # Store item data for creation
            items_to_create.append({
                'product': product,
                'variant': variant,
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': total_price,
                'product_name': product_name,
                'variant_name': variant_name
            })
        
        # Create order with total_amount
        order = Order.objects.create(
            **validated_data,
            total_amount=total_amount
        )
        
        # Create OrderItems
        for item_data in items_to_create:
            OrderItem.objects.create(
                order=order,
                **item_data
            )
        
        return order


class ContactMessageSerializer(serializers.ModelSerializer):
    """
    Serializer za kontakt poruke
    """
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'phone', 'message', 'is_read', 'is_replied', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'email': {'required': False, 'allow_blank': True, 'allow_null': True},
            'phone': {'required': False, 'allow_blank': True, 'allow_null': True},
        }

    def validate(self, data):
        """
        Proveri da je bar jedno od email ili phone popunjeno
        Samo pri kreiranju, ne pri update-u
        """
        # Ako je partial update (PATCH), preskoči validaciju
        if self.partial:
            return data

        # Ako je update (PUT), uzmi postojeće vrednosti iz instance
        if self.instance:
            email = data.get('email', self.instance.email)
            phone = data.get('phone', self.instance.phone)
        else:
            # Novo kreiranje
            email = data.get('email')
            phone = data.get('phone')

        if not email and not phone:
            raise serializers.ValidationError(
                'Morate navesti bar email ili telefon.'
            )

        return data
