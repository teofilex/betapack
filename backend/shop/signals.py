from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import ProductVariant


@receiver(post_save, sender=ProductVariant)
def update_product_timestamp_on_variant_save(sender, instance, **kwargs):
    """
    Kada se ProductVariant sačuva (kreiranje ili izmena),
    automatski ažuriraj updated_at na parent Product-u.

    Ovo omogućava da Google vidi promene cena/akcija na varijantama kroz sitemap.xml
    """
    if instance.product:
        # Ažuriraj updated_at na proizvodu bez pozivanja full save()
        instance.product.updated_at = timezone.now()
        instance.product.save(update_fields=['updated_at'])


@receiver(post_delete, sender=ProductVariant)
def update_product_timestamp_on_variant_delete(sender, instance, **kwargs):
    """
    Kada se ProductVariant obriše, ažuriraj updated_at na parent Product-u
    """
    if instance.product:
        instance.product.updated_at = timezone.now()
        instance.product.save(update_fields=['updated_at'])
