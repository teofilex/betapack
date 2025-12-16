"""
Base scraper class with common functionality
"""
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from decimal import Decimal


class BaseScraper:
    """Base class for all site-specific scrapers"""

    def __init__(self, site_config: dict):
        self.site_name = site_config.get('name')
        self.base_url = site_config.get('url')
        # Default 10s delay to respect strictest robots.txt (velog.rs)
        self.crawl_delay = site_config.get('delay', 10)

        # Realistic browser headers to avoid being blocked
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'sr-RS,sr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch a page and return BeautifulSoup object
        Respects crawl delay
        """
        try:
            time.sleep(self.crawl_delay)  # Respect crawl delay

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            return BeautifulSoup(response.content, 'lxml')

        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_price(self, price_text: str) -> Optional[Decimal]:
        """
        Parse price text to Decimal
        Handles formats like: "1,200.00 RSD", "1.200,00 din", etc.
        """
        if not price_text:
            return None

        # Remove currency symbols and letters
        cleaned = ''.join(c for c in price_text if c.isdigit() or c in '.,')

        # Handle Serbian format (1.200,00) vs US format (1,200.00)
        if ',' in cleaned and '.' in cleaned:
            # If both present, determine which is decimal separator
            if cleaned.rindex(',') > cleaned.rindex('.'):
                # Serbian: 1.200,00
                cleaned = cleaned.replace('.', '').replace(',', '.')
            else:
                # US: 1,200.00
                cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Assume decimal separator if only one or two digits after
            parts = cleaned.split(',')
            if len(parts[-1]) <= 2:
                cleaned = cleaned.replace(',', '.')
            else:
                cleaned = cleaned.replace(',', '')

        try:
            return Decimal(cleaned)
        except:
            return None

    def scrape_products(self) -> List[Dict]:
        """
        Scrape products from the site
        Must be implemented by child classes
        """
        raise NotImplementedError("Each scraper must implement scrape_products()")
