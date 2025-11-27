from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories'
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Subcategories'
        ordering = ['category__name', 'name']
        unique_together = ['category', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    on_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Dodato: Featured proizvod
    featured = models.BooleanField(default=False, help_text="Prikaži na početnoj strani")

    # Dodato: Stock (zalihe)
    in_stock = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(default=0, help_text="Količina na lageru (0 = neograničeno)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def current_price(self):
        if self.on_sale and self.sale_price:
            return self.sale_price
        return self.price


class ProductVariant(models.Model):
    """
    Varijante proizvoda - npr. različite dimenzije za isti proizvod
    Primer: Tačna 70 može imati više dimenzija
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    name = models.CharField(max_length=100, help_text="Npr: 180×135×18mm")

    # Opciono: dodatna cena za varijantu
    price_adjustment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Dodatna cena za ovu varijantu (+/-)"
    )

    # Opciono: šifra/SKU za varijantu
    sku = models.CharField(max_length=50, blank=True)

    # Stock za varijantu
    in_stock = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = ['product', 'name']

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    @property
    def final_price(self):
        """Finalna cena varijante = osnovna cena proizvoda + adjustment"""
        base_price = self.product.current_price
        return base_price + self.price_adjustment


def get_image_storage():
    """Get the appropriate storage backend for images"""
    from django.conf import settings

    # Direktno vraćaj instancu CloudinaryMediaStorage ako je produkcija
    if not settings.DEBUG:
        from shop.storage import CloudinaryMediaStorage
        print("[MODELS] Returning CloudinaryMediaStorage instance")
        return CloudinaryMediaStorage()
    else:
        from django.core.files.storage import default_storage
        print("[MODELS] Returning default_storage")
        return default_storage


class ProductImage(models.Model):
    """
    Slike proizvoda - više slika po proizvodu
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/',
        storage=get_image_storage
    )
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False, help_text="Glavna slika")
    order = models.IntegerField(default=0, help_text="Redosled prikaza")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'order', 'created_at']

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"

    def save(self, *args, **kwargs):
        # Ako je ova slika primary, ostale za isti proizvod više nisu
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)


# Validator za srpski broj telefona
phone_validator = RegexValidator(
    regex=r'^(\+381|0)[0-9]{8,9}$',
    message="Unesite ispravan broj telefona (npr: 0641234567 ili +381641234567)"
)


class Order(models.Model):
    """
    Narudžbine
    """
    STATUS_CHOICES = [
        ('pending', 'Na čekanju'),
        ('confirmed', 'Potvrđena'),
        ('processing', 'U obradi'),
        ('completed', 'Završena'),
        ('cancelled', 'Otkazana'),
    ]

    # Kontakt podaci kupca
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(
        max_length=20,
        validators=[phone_validator],
        help_text="Obavezan broj telefona"
    )
    customer_email = models.EmailField(blank=True, null=True, help_text="Opciono")

    # Adresa dostave (obavezno)
    delivery_address = models.TextField(
        default='',
        help_text="Adresa dostave je obavezna"
    )

    # Status i napomene
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True, help_text="Napomena kupca")
    admin_notes = models.TextField(blank=True, help_text="Interne napomene")

    # Totali
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Notifikacije poslate
    sms_sent = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Narudžbina #{self.id} - {self.customer_name}"


class OrderItem(models.Model):
    """
    Stavke narudžbine
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items'
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
        help_text="Odabrana varijanta/dimenzija"
    )

    quantity = models.PositiveIntegerField(default=1)

    # Snapshot cene u momentu narudžbine
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Snapshot naziva (ako se proizvod obriše kasnije)
    product_name = models.CharField(max_length=200)
    variant_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        variant_info = f" ({self.variant_name})" if self.variant_name else ""
        return f"{self.product_name}{variant_info} x{self.quantity}"

    def save(self, *args, **kwargs):
        # Auto-calculate total_price
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    """
    Kontakt poruke sa kontakt forme
    """
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(
        max_length=20,
        validators=[phone_validator],
        blank=True,
        null=True
    )
    message = models.TextField()

    # Status
    is_read = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Kontakt poruka'
        verbose_name_plural = 'Kontakt poruke'

    def clean(self):
        from django.core.exceptions import ValidationError
        super().clean()
        # Bar jedno od njih mora biti popunjeno
        if not self.email and not self.phone:
            raise ValidationError('Morate navesti bar email ili telefon.')

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"
