# Generated manually

from django.db import migrations, models


def migrate_delivery_address_to_address_city(apps, schema_editor):
    """Migrira podatke iz delivery_address u address i city"""
    Order = apps.get_model('shop', 'Order')
    for order in Order.objects.all():
        if order.delivery_address:
            # Pokušaj da parsiraj adresu - ako ima zarez, uzmi poslednji deo kao grad
            parts = order.delivery_address.split(',')
            if len(parts) > 1:
                order.address = ','.join(parts[:-1]).strip()
                order.city = parts[-1].strip()
            else:
                # Ako nema zarez, stavi sve u address, grad ostavi prazan
                order.address = order.delivery_address.strip()
                order.city = 'Beograd'  # Default grad
            order.save()


def reverse_migrate(apps, schema_editor):
    """Reverse migracija - spaja address i city u delivery_address"""
    Order = apps.get_model('shop', 'Order')
    for order in Order.objects.all():
        if order.address and order.city:
            order.delivery_address = f"{order.address}, {order.city}"
        elif order.address:
            order.delivery_address = order.address
        elif order.city:
            order.delivery_address = order.city
        else:
            order.delivery_address = ''
        order.save()


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0016_add_length_per_unit_to_variant'),
    ]

    operations = [
        # Add new fields (nullable first)
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.CharField(blank=True, default='', help_text='Ulica i broj (obavezno)', max_length=200),
        ),
        migrations.AddField(
            model_name='order',
            name='city',
            field=models.CharField(blank=True, default='', help_text='Grad (obavezno, samo Republika Srbija)', max_length=100),
        ),
        # Migrate data
        migrations.RunPython(migrate_delivery_address_to_address_city, reverse_migrate),
        # Make fields required
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.CharField(help_text='Ulica i broj (obavezno)', max_length=200),
        ),
        migrations.AlterField(
            model_name='order',
            name='city',
            field=models.CharField(help_text='Grad (obavezno, samo Republika Srbija)', max_length=100),
        ),
        # Remove old field
        migrations.RemoveField(
            model_name='order',
            name='delivery_address',
        ),
    ]

