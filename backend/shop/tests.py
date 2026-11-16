import xml.etree.ElementTree as ET
from decimal import Decimal

from django.core.cache import caches
from django.test import TestCase, TransactionTestCase, override_settings

from .models import Category, Product, ProductImage, ProductVariant

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


TEST_CACHES = {
    'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'},
    'products': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'tests-products'},
}


@override_settings(ALLOWED_HOSTS=['api.betapack.co.rs', 'testserver'], CACHES=TEST_CACHES)
class ProductListTests(TestCase):
    """Lista proizvoda: broj SQL upita, cene iz varijanti i poništavanje keša."""

    @classmethod
    def setUpTestData(cls):
        cls.cat = Category.objects.create(store='steel', name='Profili')
        cls.products = []
        for i in range(12):
            product = Product.objects.create(
                store='steel', name=f'Profil {i}', description='x', category=cls.cat, price=100 + i,
            )
            ProductVariant.objects.create(product=product, name='20x20', price=50 + i)
            ProductVariant.objects.create(product=product, name='30x30', price=70 + i, on_sale=(i % 3 == 0), sale_price=60 + i)
            ProductImage.objects.create(product=product, image=f'products/p{i}', is_primary=True)
            cls.products.append(product)

    def setUp(self):
        caches['products'].clear()

    def get_list(self, store='steel'):
        response = self.client.get(f'/api/products/?store={store}', HTTP_HOST='api.betapack.co.rs')
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_query_count_does_not_grow_with_number_of_products(self):
        # Proizvodi + slike + varijante. Ranije je svaki proizvod pravio ~3 upita za cene (N+1).
        with self.assertNumQueries(3):
            self.assertEqual(len(self.get_list()), 12)

    def test_second_request_is_served_from_cache(self):
        self.get_list()
        with self.assertNumQueries(0):
            self.assertEqual(len(self.get_list()), 12)

    def test_variant_prices_match_model_properties(self):
        # Cene u listi moraju biti iste kao one koje racuna model (svojstva Product)
        data = {p['id']: p for p in self.get_list()}
        for product in Product.objects.all():
            got = data[product.id]
            self.assertEqual(Decimal(got['min_price']), product.min_price)
            self.assertEqual(got['has_sale_variants'], product.has_sale_variants)
            expected_original = product.original_min_price
            self.assertEqual(
                got['original_min_price'],
                None if expected_original is None else f'{expected_original:.2f}',
            )

    def test_changing_product_price_invalidates_cache(self):
        product = self.products[1]
        self.assertEqual(
            {p['id']: p for p in self.get_list()}[product.id]['current_price'], '101.00',
        )
        with self.captureOnCommitCallbacks(execute=True):
            product.price = 555
            product.save()
        self.assertEqual(
            {p['id']: p for p in self.get_list()}[product.id]['current_price'], '555.00',
        )

    def test_changing_variant_price_invalidates_cache(self):
        product = self.products[1]
        self.get_list()
        variant = product.variants.get(name='20x20')
        with self.captureOnCommitCallbacks(execute=True):
            variant.price = 5
            variant.save()
        self.assertEqual(
            {p['id']: p for p in self.get_list()}[product.id]['min_price'], '5.00',
        )

    def test_deleting_variant_and_image_invalidates_cache(self):
        product = self.products[2]
        self.get_list()
        with self.captureOnCommitCallbacks(execute=True):
            product.images.all().delete()
        self.assertEqual({p['id']: p for p in self.get_list()}[product.id]['images'], [])
        with self.captureOnCommitCallbacks(execute=True):
            product.variants.all().delete()
        self.assertEqual({p['id']: p for p in self.get_list()}[product.id]['variants'], [])

    def test_category_rename_and_new_product_invalidate_cache(self):
        self.get_list()
        with self.captureOnCommitCallbacks(execute=True):
            self.cat.name = 'Novi naziv'
            self.cat.save()
        self.assertEqual({p['category_name'] for p in self.get_list()}, {'Novi naziv'})
        with self.captureOnCommitCallbacks(execute=True):
            Product.objects.create(store='steel', name='Novi', description='x', category=self.cat, price=1)
        self.assertEqual(len(self.get_list()), 13)

    def test_stores_are_cached_separately(self):
        amb_cat = Category.objects.create(store='ambalaza', name='Posude')
        Product.objects.create(store='ambalaza', name='Posuda', description='x', category=amb_cat, price=1)
        self.assertEqual(len(self.get_list('steel')), 12)
        self.assertEqual({p['store'] for p in self.get_list('ambalaza')}, {'ambalaza'})

    def test_unknown_store_and_extra_filters_bypass_cache(self):
        self.assertEqual(self.get_list('nepostojeca'), [])
        # cache-buster '_' iz starijeg frontenda ne sme da zaobilazi kes
        self.get_list()
        with self.assertNumQueries(0):
            response = self.client.get('/api/products/?store=steel&_=123', HTTP_HOST='api.betapack.co.rs')
            self.assertEqual(response.status_code, 200)


class ThrottleStaysInactiveTests(TestCase):
    def test_default_cache_is_still_dummy(self):
        # DRF throttling cuva brojace u 'default' kesu. Pravi kes tu bi ukljucio limit od
        # 100 zahteva/sat po IP adresi (iza proxy-ja svi posetioci dele jedan brojac).
        from django.conf import settings
        self.assertTrue(settings.CACHES['default']['BACKEND'].endswith('DummyCache'))


@override_settings(ALLOWED_HOSTS=['api.betapack.co.rs', 'testserver'], CACHES=TEST_CACHES)
class ProductCacheCommitTests(TransactionTestCase):
    """Bez captureOnCommitCallbacks: izmena u bazi stvarno poništava kes (kao u produkciji)."""

    def test_price_change_is_visible_right_after_save(self):
        caches['products'].clear()
        category = Category.objects.create(store='steel', name='Profili')
        product = Product.objects.create(store='steel', name='Profil', description='x', category=category, price=100)
        url = '/api/products/?store=steel'
        first = self.client.get(url, HTTP_HOST='api.betapack.co.rs').json()
        self.assertEqual(first[0]['current_price'], '100.00')
        product.price = 250
        product.save()
        second = self.client.get(url, HTTP_HOST='api.betapack.co.rs').json()
        self.assertEqual(second[0]['current_price'], '250.00')
