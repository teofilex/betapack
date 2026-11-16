from django.contrib.sitemaps import Sitemap
from .models import Product, Category

# Sajt (frontend) je na www domenu. Sitemap se servira sa API-ja (preko Vercel rewrite-a),
# pa domen ne sme da zavisi od hosta zahteva.
FRONTEND_DOMAIN = 'www.betapack.co.rs'


class FrontendSitemap(Sitemap):
    """Osnova za sve sitemap-ove: https + www domen, bez obzira na host zahteva."""
    protocol = 'https'

    def get_domain(self, site=None):
        return FRONTEND_DOMAIN


# Putanje moraju biti iste kao canonical na stranama: /<prodavnica> bez kose crte
# na kraju, kategorije kao /<prodavnica>?category=N, proizvodi pod svojom prodavnicom.
class ProductSitemap(FrontendSitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Product.objects.filter(in_stock=True)

    def lastmod(self, obj):
        # Koristi updated_at da Google zna kada je proizvod poslednji put izmenjen (cena, opis, itd)
        return obj.updated_at

    def location(self, obj):
        # Koristi slug ako postoji, inače ID (backward compatibility)
        identifier = obj.slug if obj.slug else obj.id
        # URL-ovi su od uvođenja ambalaže razdvojeni po prodavnici: /steel/... i /ambalaza/...
        store = obj.store or 'steel'
        return f'/{store}/proizvod/{identifier}'


class CategorySitemap(FrontendSitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        # Za sada koristi query parameter (kasnije može slug)
        store = obj.store or 'steel'
        return f'/{store}?category={obj.id}'


class StaticViewSitemap(FrontendSitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        # Početna je od uvođenja ambalaže razdelnik ka dvema prodavnicama,
        # pa svaka prodavnica ima svoju ponudu, o-nama i kontakt stranicu.
        paths = ['/']
        for store in ('steel', 'ambalaza'):
            paths += [f'/{store}', f'/{store}/o-nama', f'/{store}/kontakt']
        return paths

    def location(self, item):
        return item
