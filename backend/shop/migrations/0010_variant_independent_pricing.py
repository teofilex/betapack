# Generated migration for ProductVariant independent pricing

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_alter_productimage_image'),
    ]

    operations = [
        # Add new price field to ProductVariant
        migrations.AddField(
            model_name='productvariant',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Osnovna cena ove varijante', max_digits=10),
            preserve_default=False,
        ),
        # Add on_sale field to ProductVariant
        migrations.AddField(
            model_name='productvariant',
            name='on_sale',
            field=models.BooleanField(default=False, help_text='Da li je varijanta na akciji'),
        ),
        # Add sale_price field to ProductVariant
        migrations.AddField(
            model_name='productvariant',
            name='sale_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Akcijska cena varijante', max_digits=10, null=True),
        ),
        # Remove old price_adjustment field
        migrations.RemoveField(
            model_name='productvariant',
            name='price_adjustment',
        ),
    ]
