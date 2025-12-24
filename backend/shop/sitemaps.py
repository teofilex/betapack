from django.contrib.sitemaps import Sitemap
from .models import Product, Category


class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Product.objects.filter(in_stock=True)

    def lastmod(self, obj):
        # Koristi updated_at da Google zna kada je proizvod poslednji put izmenjen (cena, opis, itd)
        return obj.updated_at

    def location(self, obj):
        # Koristi slug ako postoji, inače ID (backward compatibility)
        identifier = obj.slug if obj.slug else obj.id
        return f'/proizvod/{identifier}'


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6
    protocol = 'https'

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        # Za sada koristi query parameter (kasnije može slug)
        return f'/?category={obj.id}'


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        return ['home', 'about', 'contact']

    def location(self, item):
        if item == 'home':
            return '/'
        elif item == 'about':
            return '/o-nama'
        elif item == 'contact':
            return '/kontakt'
        return f'/{item}'
