from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0026_add_store_and_selling_modes'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariant',
            name='selling_mode',
            field=models.CharField(
                blank=True,
                choices=[
                    ('piece', 'Po komadu'),
                    ('length', 'Po metraži'),
                    ('package', 'Po pakovanju'),
                    ('weight', 'Po kilogramu'),
                    ('on_request', 'Na upit'),
                ],
                default='piece',
                help_text='Način prodaje ove varijante',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='package_size',
            field=models.PositiveIntegerField(
                default=1,
                help_text='Broj komada u pakovanju (za prodaju po pakovanju)',
            ),
        ),
    ]
