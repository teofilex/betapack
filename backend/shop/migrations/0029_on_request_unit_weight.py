from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0028_add_on_request_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='on_request_unit',
            field=models.CharField(
                blank=True,
                choices=[('piece', 'Po komadu'), ('package', 'Po pakovanju'), ('weight', 'Po kilogramu')],
                default='piece',
                help_text='Jedinica prodaje kada je cena na upit',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='on_request_unit',
            field=models.CharField(
                blank=True,
                choices=[('piece', 'Po komadu'), ('package', 'Po pakovanju'), ('weight', 'Po kilogramu')],
                default='piece',
                help_text='Jedinica prodaje kada je cena na upit',
                max_length=20,
            ),
        ),
    ]
