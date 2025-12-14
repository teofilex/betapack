# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_alter_productvariant_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sold_by_length',
            field=models.BooleanField(default=False, help_text='Proizvod se prodaje po metraži (1 komad = 6m)'),
        ),
    ]



