from django.contrib.sitemaps import Sitemap
from .models import Product, Category


class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Product.objects.filter(in_stock=True)

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return f'/product/{obj.id}'


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6
    protocol = 'https'

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return f'/category/{obj.id}'


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        return ['home', 'about', 'contact']

    def location(self, item):
        if item == 'home':
            return '/'
        return f'/{item}'
