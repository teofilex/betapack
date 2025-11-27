# Generated migration for ProductImage.image storage field

from django.db import migrations, models
import shop.models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_alter_contactmessage_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(storage=shop.models.get_image_storage, upload_to='products/%Y/%m/'),
        ),
    ]
