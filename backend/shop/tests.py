import xml.etree.ElementTree as ET

from django.test import TestCase, override_settings

from .models import Category, Product

SITEMAP_NS = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}


@override_settings(ALLOWED_HOSTS=['api.betapack.co.rs', 'testserver'])
class SitemapTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.steel_cat = Category.objects.create(store='steel', name='Profili')
        cls.amb_cat = Category.objects.create(store='ambalaza', name='Posude')
        Product.objects.create(
            store='steel', name='Kutija 20x20', description='x', category=cls.steel_cat, price=100,
        )
        Product.objects.create(
            store='ambalaza', name='PP posuda 500', description='x', category=cls.amb_cat, price=10,
        )
        Product.objects.create(
            store='steel', name='Nema na stanju', description='x', category=cls.steel_cat,
            price=100, in_stock=False,
        )

    def sitemap_locations(self):
        # Host zahteva (API domen) ne sme da procuri u URL-ove
        response = self.client.get('/sitemap.xml', HTTP_HOST='api.betapack.co.rs')
        self.assertEqual(response.status_code, 200)
        root = ET.fromstring(response.content)
        return [loc.text for loc in root.findall('sm:url/sm:loc', SITEMAP_NS)]

    def test_all_urls_use_www_https_domain(self):
        locations = self.sitemap_locations()
        self.assertTrue(locations)
        for loc in locations:
            self.assertTrue(loc.startswith('https://www.betapack.co.rs/'), loc)

    def test_no_trailing_slash_after_store_path(self):
        for loc in self.sitemap_locations():
            self.assertNotIn('/steel/?', loc)
            self.assertNotIn('/ambalaza/?', loc)
            self.assertFalse(loc.endswith('/steel/') or loc.endswith('/ambalaza/'), loc)

    def test_static_pages(self):
        locations = self.sitemap_locations()
        for path in (
            '/', '/steel', '/steel/o-nama', '/steel/kontakt',
            '/ambalaza', '/ambalaza/o-nama', '/ambalaza/kontakt',
        ):
            self.assertIn(f'https://www.betapack.co.rs{path}', locations)

    def test_categories_use_store_path_with_query(self):
        locations = self.sitemap_locations()
        self.assertIn(f'https://www.betapack.co.rs/steel?category={self.steel_cat.id}', locations)
        self.assertIn(f'https://www.betapack.co.rs/ambalaza?category={self.amb_cat.id}', locations)

    def test_products_are_under_their_own_store(self):
        locations = self.sitemap_locations()
        self.assertIn('https://www.betapack.co.rs/steel/proizvod/kutija-20x20', locations)
        self.assertIn('https://www.betapack.co.rs/ambalaza/proizvod/pp-posuda-500', locations)

    def test_out_of_stock_products_are_skipped(self):
        locations = self.sitemap_locations()
        self.assertFalse([loc for loc in locations if 'nema-na-stanju' in loc])


@override_settings(ALLOWED_HOSTS=['api.betapack.co.rs', 'testserver'])
class RobotsTests(TestCase):
    def test_api_stays_crawlable_everything_else_blocked(self):
        # Googlebot mora da stigne do /api/ da bi renderovao frontend
        response = self.client.get('/robots.txt', HTTP_HOST='api.betapack.co.rs')
        self.assertEqual(response.status_code, 200)
        lines = response.content.decode().splitlines()
        self.assertEqual(lines, [
            'User-agent: *',
            'Allow: /api/',
            'Disallow: /admin/',
            'Disallow: /',
        ])

    def test_no_sitemap_line(self):
        response = self.client.get('/robots.txt', HTTP_HOST='api.betapack.co.rs')
        self.assertNotIn('Sitemap', response.content.decode())
