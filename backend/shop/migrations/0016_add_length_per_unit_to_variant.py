# Migration to add length_per_unit to ProductVariant

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0014_alter_product_length_per_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariant',
            name='length_per_unit',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Dužina 1 komada u metrima za ovu varijantu (npr. 4.0 za 4m). Ako nije postavljeno, koristi se dužina iz proizvoda.',
                max_digits=10,
                null=True
            ),
        ),
    ]



