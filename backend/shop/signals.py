from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .cache import invalidate_products_cache
from .models import Category, Product, ProductImage, ProductVariant, Subcategory


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


# Lista proizvoda je kesirana: sve sto utice na njen sadrzaj poništava kes.
# Product i ProductVariant (varijanta pri cuvanju dira i proizvod) menjaju cene,
# ProductImage slike, a Category/Subcategory imena koja se prikazuju uz proizvod.
for _model in (Product, ProductVariant, ProductImage, Category, Subcategory):
    post_save.connect(invalidate_products_cache, sender=_model, dispatch_uid=f'products-cache-save-{_model.__name__}')
    post_delete.connect(invalidate_products_cache, sender=_model, dispatch_uid=f'products-cache-delete-{_model.__name__}')
