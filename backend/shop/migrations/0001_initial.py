# Generated manually - Complete initial migration

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=models.CASCADE, related_name='subcategories', to='shop.category')),
            ],
            options={
                'verbose_name_plural': 'Subcategories',
                'ordering': ['category__name', 'name'],
                'unique_together': {('category', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('on_sale', models.BooleanField(default=False)),
                ('sale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('featured', models.BooleanField(default=False, help_text='Prikaži na početnoj strani')),
                ('in_stock', models.BooleanField(default=True)),
                ('stock_quantity', models.IntegerField(default=0, help_text='Količina na lageru (0 = neograničeno)')),
                ('sold_by_length', models.BooleanField(default=False, help_text='Proizvod se prodaje po metraži')),
                ('length_per_unit', models.DecimalField(blank=True, decimal_places=2, default=6.0, help_text='Dužina 1 komada u metrima (npr. 6.0 za 6m)', max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=models.CASCADE, related_name='products', to='shop.category')),
                ('subcategory', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='products', to='shop.subcategory')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Npr: 180×135×18mm', max_length=100)),
                ('price', models.DecimalField(decimal_places=2, help_text='Osnovna cena ove varijante', max_digits=10)),
                ('on_sale', models.BooleanField(default=False, help_text='Da li je varijanta na akciji')),
                ('sale_price', models.DecimalField(blank=True, decimal_places=2, help_text='Akcijska cena varijante', max_digits=10, null=True)),
                ('sku', models.CharField(blank=True, max_length=50)),
                ('in_stock', models.BooleanField(default=True)),
                ('stock_quantity', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=models.CASCADE, related_name='variants', to='shop.product')),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('product', 'name')},
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products/%Y/%m/')),
                ('alt_text', models.CharField(blank=True, max_length=200)),
                ('is_primary', models.BooleanField(default=False, help_text='Glavna slika')),
                ('order', models.IntegerField(default=0, help_text='Redosled prikaza')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=models.CASCADE, related_name='images', to='shop.product')),
            ],
            options={
                'ordering': ['-is_primary', 'order', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=200)),
                ('customer_phone', models.CharField(help_text='Obavezan broj telefona', max_length=20, validators=[django.core.validators.RegexValidator(message='Unesite ispravan broj telefona (npr: 0641234567 ili +381641234567)', regex='^(\\+381|0)[0-9]{8,9}$')])),
                ('customer_email', models.EmailField(blank=True, help_text='Opciono', null=True)),
                ('delivery_address', models.TextField(default='', help_text='Adresa dostave je obavezna')),
                ('status', models.CharField(choices=[('pending', 'Na čekanju'), ('confirmed', 'Potvrđena'), ('processing', 'U obradi'), ('completed', 'Završena'), ('cancelled', 'Otkazana')], default='pending', max_length=20)),
                ('notes', models.TextField(blank=True, help_text='Napomena kupca', null=True)),
                ('admin_notes', models.TextField(blank=True, help_text='Interne napomene')),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sms_sent', models.BooleanField(default=False)),
                ('email_sent', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, default=1, help_text='Količina (može biti decimalna za proizvode po metraži)', max_digits=10)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('product_name', models.CharField(max_length=200)),
                ('variant_name', models.CharField(blank=True, max_length=100)),
                ('order', models.ForeignKey(on_delete=models.CASCADE, related_name='items', to='shop.order')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='order_items', to='shop.product')),
                ('variant', models.ForeignKey(blank=True, help_text='Odabrana varijanta/dimenzija', null=True, on_delete=models.SET_NULL, related_name='order_items', to='shop.productvariant')),
            ],
        ),
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(blank=True, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True, validators=[django.core.validators.RegexValidator(message='Unesite ispravan broj telefona (npr: 0641234567 ili +381641234567)', regex='^(\\+381|0)[0-9]{8,9}$')])),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('is_replied', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Kontakt poruka',
                'verbose_name_plural': 'Kontakt poruke',
                'ordering': ['-created_at'],
            },
        ),
    ]
