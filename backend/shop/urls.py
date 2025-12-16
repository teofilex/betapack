from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    current_user,
    CategoryViewSet,
    SubcategoryViewSet,
    ProductViewSet,
    ProductVariantViewSet,
    ProductImageViewSet,
    OrderViewSet,
    ContactMessageViewSet,
    contact_message
)
from .views_scraping import CompetitorSiteViewSet, ScrapedProductViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('subcategories', SubcategoryViewSet, basename='subcategory')
router.register('products', ProductViewSet, basename='product')
router.register('product-variants', ProductVariantViewSet, basename='product-variant')
router.register('product-images', ProductImageViewSet, basename='product-image')
router.register('orders', OrderViewSet, basename='order')
router.register('contact-messages', ContactMessageViewSet, basename='contact-message')
router.register('competitor-sites', CompetitorSiteViewSet, basename='competitor-site')
router.register('scraped-products', ScrapedProductViewSet, basename='scraped-product')

urlpatterns = [
    path('auth/user/', current_user, name='current_user'),
    path('orders/notifications/', views.order_notifications_stream, name='order-notifications'),
    path('contact/', contact_message, name='contact-message'),
    path('', include(router.urls)),
]