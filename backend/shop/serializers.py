from rest_framework import serializers
from .models import Category, Subcategory, Product, ProductVariant, ProductImage, Order, OrderItem


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
        # Vrati relativni URL slike
        if obj.image and obj.image.name:
            try:
                url = obj.image.url
                # Django ImageField.url već vraća /media/products/...
                if url.startswith('/media/'):
                    return url
                elif url.startswith('media/'):
                    return '/' + url
                elif url.startswith('/'):
                    return '/media' + url if not url.startswith('/media') else url
                else:
                    return '/media/' + url
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
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'name', 'price_adjustment', 'final_price', 'sku',
            'in_stock', 'stock_quantity', 'created_at'
        ]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'on_sale', 'sale_price',
            'category', 'category_name', 'subcategory', 'subcategory_name',
            'current_price', 'featured', 'in_stock', 'stock_quantity',
            'variants', 'images', 'created_at', 'updated_at'
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True, allow_null=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True, allow_null=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'product', 'product_name', 'variant', 'variant_name',
            'quantity', 'unit_price', 'total_price'
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'customer_phone', 'customer_email',
            'delivery_address', 'notes', 'status', 'total_amount',
            'items', 'created_at', 'updated_at'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )

    class Meta:
        model = Order
        fields = [
            'customer_name', 'customer_phone', 'customer_email',
            'delivery_address', 'notes', 'items'
        ]
        extra_kwargs = {
            'customer_name': {'required': True},
            'customer_phone': {'required': True},
            'customer_email': {'allow_null': True, 'allow_blank': True, 'required': False},
            'delivery_address': {'allow_null': True, 'allow_blank': True, 'required': False},
            'notes': {'allow_null': True, 'allow_blank': True, 'required': False},
        }
    
    def validate(self, data):
        # Konvertuj prazne stringove u None za opciona polja
        if 'customer_email' in data and data['customer_email'] == '':
            data['customer_email'] = None
        if 'delivery_address' in data and data['delivery_address'] == '':
            data['delivery_address'] = None
        if 'notes' in data and data['notes'] == '':
            data['notes'] = None
        return data
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # First calculate total_amount
        total_amount = 0
        items_to_create = []
        
        for item_data in items_data:
            product_id = item_data.get('product') or item_data.get('product_id')
            variant_id = item_data.get('variant') or item_data.get('variant_id')
            quantity = item_data.get('quantity', 1)
            
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
