"""
Scraper for JeepCommerce.rs (WooCommerce site)
"""
from typing import List, Dict
from .base import BaseScraper
import re


class JeepCommerceScraper(BaseScraper):
    """
    Scraper for https://jeepcommerce.rs/
    """

    def __init__(self):
        config = {
            'name': 'JeepCommerce',
            'url': 'https://jeepcommerce.rs',
            'delay': 10
        }
        super().__init__(config)

        self.categories = [
            {'name': 'Profili', 'url': '/kategorija-proizvoda/profili/'},
            {'name': 'Limovi', 'url': '/kategorija-proizvoda/limovi/'},
            {'name': 'Cevi', 'url': '/kategorija-proizvoda/cevi/'},
        ]

    def scrape_products(self) -> List[Dict]:
        all_products = []

        print(f"🕷️  Starting scrape of {self.site_name}...")
        print(f"⏱️  Crawl delay: {self.crawl_delay}s")

        for category in self.categories:
            print(f"\n📁 Category: {category['name']}")
            
            category_url = f"{self.base_url}{category['url']}"
            soup = self.fetch_page(category_url)

            if not soup:
                print(f"⚠️  Failed to fetch {category['name']}")
                continue

            # WooCommerce structure
            products = soup.select('.product')
            print(f"   Found {len(products)} products")

            for product_elem in products:
                try:
                    product = self._extract_product_data(product_elem, category['name'])
                    if product:
                        all_products.append(product)
                        status_icon = "🔥" if product['on_sale'] else "✅"
                        print(f"   {status_icon} {product['name'][:40]:<40} - {product['current_price']} RSD")
                except Exception as e:
                    print(f"   ⚠️  Error: {e}")
                    continue

        print(f"\n📊 Total: {len(all_products)}")
        return all_products

    def _extract_product_data(self, elem, category_name: str) -> Dict:
        # Link i ID
        link_elem = elem.select_one('a.woocommerce-LoopProduct-link')
        if not link_elem:
            return None

        product_url = link_elem.get('href', '')
        
        # Extract ID from URL
        id_match = re.search(r'/proizvod/([^/]+)/', product_url) or re.search(r'product/([^/]+)/', product_url)
        external_id = id_match.group(1) if id_match else product_url.split('/')[-2]

        # Name
        name_elem = elem.select_one('.woocommerce-loop-product__title') or elem.select_one('h2')
        name = name_elem.get_text(strip=True) if name_elem else 'Unknown'

        # Price
        price_elem = elem.select_one('.price ins .amount') or elem.select_one('.price .amount')
        price_text = price_elem.get_text(strip=True) if price_elem else ''
        current_price = self.parse_price(price_text)

        if not current_price:
            return None

        # Check if on sale
        on_sale = elem.select_one('.onsale') is not None

        # Image
        img_elem = elem.select_one('img')
        image_url = ''
        if img_elem:
            image_url = img_elem.get('src', '') or img_elem.get('data-src', '')

        return {
            'external_id': external_id,
            'name': name,
            'category': category_name,
            'description': '',
            'current_price': current_price,
            'on_sale': on_sale,
            'sale_price': current_price if on_sale else None,
            'original_price': None,
            'product_url': product_url,
            'image_url': image_url,
            'in_stock': True
        }
