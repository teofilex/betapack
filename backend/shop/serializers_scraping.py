"""
Serializers for scraping data
"""
from rest_framework import serializers
from .models_scraping import CompetitorSite, ScrapedProduct, PriceHistory


class CompetitorSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitorSite
        fields = ['id', 'name', 'url', 'is_active', 'last_scraped_at', 'last_scrape_status']


class ScrapedProductSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source='site.name', read_only=True)
    discount_percentage = serializers.ReadOnlyField()
    effective_price = serializers.ReadOnlyField()

    class Meta:
        model = ScrapedProduct
        fields = [
            'id', 'site', 'site_name', 'external_id', 'name', 'category',
            'description', 'current_price', 'on_sale', 'sale_price',
            'original_price', 'effective_price', 'discount_percentage',
            'product_url', 'image_url', 'in_stock', 'first_seen_at', 'last_seen_at'
        ]


class PriceHistorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = PriceHistory
        fields = ['id', 'product', 'product_name', 'price', 'on_sale', 'sale_price', 'in_stock', 'recorded_at']
