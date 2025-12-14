# Modified to add length_per_unit field instead of altering it

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0013_alter_orderitem_quantity_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='length_per_unit',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                default=6.0,
                help_text='Dužina 1 komada u metrima (npr. 6.0 za 6m)',
                max_digits=10
            ),
        ),
    ]
