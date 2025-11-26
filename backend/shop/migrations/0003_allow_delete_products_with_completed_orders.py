# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_order_product_featured_product_in_stock_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='order_items',
                to='shop.product'
            ),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='variant',
            field=models.ForeignKey(
                blank=True,
                help_text='Odabrana varijanta/dimenzija',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='order_items',
                to='shop.productvariant'
            ),
        ),
    ]


