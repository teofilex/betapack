"""
Scraper for Hanan.rs
"""
from typing import List, Dict
from .base import BaseScraper
import re

class HananScraper(BaseScraper):
    def __init__(self):
        config = {'name': 'Hanan', 'url': 'https://hanan.rs', 'delay': 10}
        super().__init__(config)
        self.categories = [
            {'name': 'Kovani elementi', 'url': '/kategorija-proizvoda/kovani-elementi/'},
        ]

    def scrape_products(self) -> List[Dict]:
        all_products = []
        print(f"🕷️  {self.site_name} - Crawl delay: {self.crawl_delay}s")

        for category in self.categories:
            print(f"\n📁 {category['name']}")

            # Scrape all pages for this category
            page_num = 1
            while True:
                # Build URL for current page
                if page_num == 1:
                    page_url = f"{self.base_url}{category['url']}"
                else:
                    # Remove trailing slash and add /page/N/
                    base_cat_url = category['url'].rstrip('/')
                    page_url = f"{self.base_url}{base_cat_url}/page/{page_num}/"

                print(f"   📄 Page {page_num}: {page_url}")
                soup = self.fetch_page(page_url)

                if not soup:
                    print(f"   ⚠️  Failed to fetch page {page_num}")
                    break

                # Find products on this page
                products_on_page = soup.select('.product')

                if not products_on_page:
                    print(f"   ℹ️  No products found on page {page_num}, stopping")
                    break

                print(f"   📦 Found {len(products_on_page)} products on page {page_num}")

                # Extract product data
                for elem in products_on_page:
                    try:
                        link = elem.select_one('a.woocommerce-LoopProduct-link')
                        if not link: continue
                        url = link.get('href', '')
                        id_match = re.search(r'/([^/]+)/?$', url)
                        name_elem = elem.select_one('.woocommerce-loop-product__title') or elem.select_one('h2')
                        price_elem = elem.select_one('.price ins .amount') or elem.select_one('.price .amount')
                        price = self.parse_price(price_elem.get_text(strip=True) if price_elem else '')
                        if not price: continue
                        all_products.append({
                            'external_id': id_match.group(1) if id_match else url.split('/')[-2],
                            'name': name_elem.get_text(strip=True) if name_elem else 'Unknown',
                            'category': category['name'],
                            'description': '',
                            'current_price': price,
                            'on_sale': elem.select_one('.onsale') is not None,
                            'sale_price': price if elem.select_one('.onsale') else None,
                            'original_price': None,
                            'product_url': url,
                            'image_url': (elem.select_one('img').get('src', '') if elem.select_one('img') else ''),
                            'in_stock': True
                        })
                        print(f"      ✅ {all_products[-1]['name'][:40]:<40} - {price} RSD")
                    except Exception as e:
                        print(f"      ⚠️  {e}")

                page_num += 1

        print(f"\n📊 Total: {len(all_products)}")
        return all_products
