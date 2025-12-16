"""
Django management command to scrape competitor websites

Usage:
    python manage.py scrape_competitors
    python manage.py scrape_competitors --site joilart
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from shop.models_scraping import CompetitorSite, ScrapedProduct, PriceHistory, ScrapeLog
from shop.scrapers import (
    JoilArtScraper,
    JeepCommerceScraper,
    HananScraper,
    VelogScraper,
    IronWorksScraper
)


class Command(BaseCommand):
    help = 'Scrape competitor websites for product prices'

    def add_arguments(self, parser):
        parser.add_argument(
            '--site',
            type=str,
            help='Specific site to scrape (e.g., joilart)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force scrape even if not due',
        )

    def handle(self, *args, **options):
        site_name = options.get('site')
        force = options.get('force', False)

        if site_name:
            # Scrape specific site
            try:
                site = CompetitorSite.objects.get(name__iexact=site_name)
                self.scrape_site(site, force)
            except CompetitorSite.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Site "{site_name}" not found'))
        else:
            # Scrape all active sites
            sites = CompetitorSite.objects.filter(is_active=True)

            if not force:
                sites = [s for s in sites if s.needs_scraping]

            if not sites:
                self.stdout.write(self.style.SUCCESS('No sites need scraping'))
                return

            self.stdout.write(f'Scraping {len(sites)} site(s)...')

            for site in sites:
                self.scrape_site(site, force)

    def scrape_site(self, site: CompetitorSite, force: bool = False):
        """Scrape a single competitor site"""

        if not force and not site.needs_scraping:
            self.stdout.write(
                self.style.WARNING(f'⏭️  Skipping {site.name} (not due for scraping)')
            )
            return

        self.stdout.write(f'\n🕷️  Scraping {site.name}...')

        # Create scrape log
        log = ScrapeLog.objects.create(
            site=site,
            status='started'
        )

        try:
            # Get appropriate scraper
            scraper = self.get_scraper(site.name)

            if not scraper:
                raise ValueError(f'No scraper found for {site.name}')

            # Perform scraping
            products_data = scraper.scrape_products()

            # Update database
            products_new = 0
            products_updated = 0

            for product_data in products_data:
                product, created = ScrapedProduct.objects.update_or_create(
                    site=site,
                    external_id=product_data['external_id'],
                    defaults={
                        'name': product_data['name'],
                        'category': product_data.get('category', ''),
                        'description': product_data.get('description', ''),
                        'current_price': product_data['current_price'],
                        'on_sale': product_data.get('on_sale', False),
                        'sale_price': product_data.get('sale_price'),
                        'original_price': product_data.get('original_price'),
                        'product_url': product_data['product_url'],
                        'image_url': product_data.get('image_url', ''),
                        'in_stock': product_data.get('in_stock', True),
                        'is_active': True,
                    }
                )

                if created:
                    products_new += 1
                else:
                    products_updated += 1

                # Record price history
                PriceHistory.objects.create(
                    product=product,
                    price=product_data['current_price'],
                    on_sale=product_data.get('on_sale', False),
                    sale_price=product_data.get('sale_price'),
                    in_stock=product_data.get('in_stock', True)
                )

            # Update site and log
            site.last_scraped_at = timezone.now()
            site.last_scrape_status = 'success'
            site.last_error_message = ''
            site.save()

            log.status = 'success'
            log.products_found = len(products_data)
            log.products_new = products_new
            log.products_updated = products_updated
            log.completed_at = timezone.now()
            log.duration_seconds = (log.completed_at - log.started_at).total_seconds()
            log.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ {site.name}: Found {len(products_data)}, New: {products_new}, Updated: {products_updated}'
                )
            )

        except Exception as e:
            # Handle errors
            error_msg = str(e)

            site.last_scrape_status = 'failed'
            site.last_error_message = error_msg
            site.save()

            log.status = 'failed'
            log.error_message = error_msg
            log.completed_at = timezone.now()
            log.save()

            self.stdout.write(
                self.style.ERROR(f'❌ {site.name}: {error_msg}')
            )

    def get_scraper(self, site_name: str):
        """Return appropriate scraper for site"""
        scrapers = {
            'joilart': JoilArtScraper,
            'jeepcommerce': JeepCommerceScraper,
            'hanan': HananScraper,
            'velog': VelogScraper,
            'ironworks': IronWorksScraper,
        }

        scraper_class = scrapers.get(site_name.lower())
        if scraper_class:
            return scraper_class()

        return None
