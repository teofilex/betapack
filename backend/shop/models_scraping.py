"""
Models for competitor price scraping and monitoring
"""
from django.db import models
from django.utils import timezone


class CompetitorSite(models.Model):
    """
    Competitor websites to scrape
    """
    name = models.CharField(max_length=100, unique=True, help_text="e.g., JoilArt, Jeep Commerce")
    url = models.URLField(help_text="Base URL of the competitor site")
    is_active = models.BooleanField(default=True, help_text="Enable/disable scraping for this site")

    # Scraping configuration
    scrape_interval_hours = models.IntegerField(default=24, help_text="How often to scrape (in hours)")
    crawl_delay_seconds = models.IntegerField(default=3, help_text="Delay between requests (respect robots.txt)")

    # Metadata
    last_scraped_at = models.DateTimeField(null=True, blank=True)
    last_scrape_status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('pending', 'Pending')
        ],
        default='pending'
    )
    last_error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Konkurentski sajt'
        verbose_name_plural = 'Konkurentski sajtovi'

    def __str__(self):
        return self.name

    @property
    def needs_scraping(self):
        """Check if site needs to be scraped based on interval"""
        if not self.is_active:
            return False
        if not self.last_scraped_at:
            return True
        time_since_last_scrape = timezone.now() - self.last_scraped_at
        return time_since_last_scrape.total_seconds() / 3600 >= self.scrape_interval_hours


class ScrapedProduct(models.Model):
    """
    Products scraped from competitor sites
    """
    site = models.ForeignKey(
        CompetitorSite,
        on_delete=models.CASCADE,
        related_name='scraped_products'
    )

    # Product identification
    external_id = models.CharField(
        max_length=100,
        help_text="Product ID on competitor's site"
    )
    name = models.CharField(max_length=300)
    category = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    # Pricing
    current_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Current price in RSD"
    )
    on_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Original price before discount"
    )

    # URLs and images
    product_url = models.URLField(max_length=500)
    image_url = models.URLField(max_length=500, blank=True)

    # Availability
    in_stock = models.BooleanField(default=True)

    # Metadata
    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(
        default=True,
        help_text="False if product no longer appears on competitor site"
    )

    class Meta:
        ordering = ['-last_seen_at']
        unique_together = ['site', 'external_id']
        verbose_name = 'Scraped proizvod'
        verbose_name_plural = 'Scraped proizvodi'
        indexes = [
            models.Index(fields=['site', 'external_id']),
            models.Index(fields=['category']),
            models.Index(fields=['on_sale']),
        ]

    def __str__(self):
        return f"{self.site.name} - {self.name}"

    @property
    def effective_price(self):
        """Get the actual selling price (sale price if on sale, otherwise current price)"""
        if self.on_sale and self.sale_price:
            return self.sale_price
        return self.current_price

    @property
    def discount_percentage(self):
        """Calculate discount percentage if on sale"""
        if self.on_sale and self.original_price and self.sale_price:
            discount = ((self.original_price - self.sale_price) / self.original_price) * 100
            return round(discount, 1)
        return 0


class PriceHistory(models.Model):
    """
    Historical price tracking for scraped products
    """
    product = models.ForeignKey(
        ScrapedProduct,
        on_delete=models.CASCADE,
        related_name='price_history'
    )

    # Price at this point in time
    price = models.DecimalField(max_digits=10, decimal_places=2)
    on_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Availability at this point in time
    in_stock = models.BooleanField(default=True)

    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        verbose_name = 'Istorija cena'
        verbose_name_plural = 'Istorije cena'
        indexes = [
            models.Index(fields=['product', '-recorded_at']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.price} RSD @ {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"


class ScrapeLog(models.Model):
    """
    Log of scraping operations
    """
    site = models.ForeignKey(
        CompetitorSite,
        on_delete=models.CASCADE,
        related_name='scrape_logs'
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('started', 'Started'),
            ('success', 'Success'),
            ('failed', 'Failed')
        ]
    )

    products_found = models.IntegerField(default=0)
    products_updated = models.IntegerField(default=0)
    products_new = models.IntegerField(default=0)

    error_message = models.TextField(blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Scrape log'
        verbose_name_plural = 'Scrape logs'

    def __str__(self):
        return f"{self.site.name} - {self.status} @ {self.started_at.strftime('%Y-%m-%d %H:%M')}"
