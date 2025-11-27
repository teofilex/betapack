# Generated migration for ProductVariant independent pricing

from django.db import migrations, models


def migrate_variant_prices(apps, schema_editor):
    """
    Migrate existing variant prices from price_adjustment to new price field
    """
    ProductVariant = apps.get_model('shop', 'ProductVariant')

    for variant in ProductVariant.objects.select_related('product').all():
        # Set variant price = product price + price_adjustment
        variant.price = variant.product.price + variant.price_adjustment

        # Copy sale status from product to variant
        variant.on_sale = variant.product.on_sale

        # If product is on sale, calculate variant's sale price
        if variant.product.on_sale and variant.product.sale_price:
            variant.sale_price = variant.product.sale_price + variant.price_adjustment

        variant.save()


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_alter_productimage_image'),
    ]

    operations = [
        # 1. Add new price field to ProductVariant with default
        migrations.AddField(
            model_name='productvariant',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Osnovna cena ove varijante', max_digits=10),
        ),
        # 2. Add on_sale field to ProductVariant
        migrations.AddField(
            model_name='productvariant',
            name='on_sale',
            field=models.BooleanField(default=False, help_text='Da li je varijanta na akciji'),
        ),
        # 3. Add sale_price field to ProductVariant
        migrations.AddField(
            model_name='productvariant',
            name='sale_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Akcijska cena varijante', max_digits=10, null=True),
        ),
        # 4. Migrate existing data from price_adjustment to new fields
        migrations.RunPython(migrate_variant_prices, reverse_code=migrations.RunPython.noop),
        # 5. Remove old price_adjustment field
        migrations.RemoveField(
            model_name='productvariant',
            name='price_adjustment',
        ),
    ]
