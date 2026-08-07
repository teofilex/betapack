from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0027_add_selling_mode_to_variant'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='on_request_unit',
            field=models.CharField(
                blank=True,
                choices=[('piece', 'Po komadu'), ('package', 'Po pakovanju')],
                default='piece',
                help_text='Jedinica prodaje kada je cena na upit',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='on_request_unit',
            field=models.CharField(
                blank=True,
                choices=[('piece', 'Po komadu'), ('package', 'Po pakovanju')],
                default='piece',
                help_text='Jedinica prodaje kada je cena na upit',
                max_length=20,
            ),
        ),
    ]
