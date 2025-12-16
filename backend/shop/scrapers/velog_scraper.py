"""
Scraper for Velog.rs - Crawl-delay: 10s (STRICT)
"""
from typing import List, Dict
from .base import BaseScraper
import re

class VelogScraper(BaseScraper):
    def __init__(self):
        config = {'name': 'Velog', 'url': 'https://www.velog.rs', 'delay': 10}
        super().__init__(config)
        self.categories = [
            {'name': 'Bravarski program', 'url': '/bravarski_program'},
        ]

    def scrape_products(self) -> List[Dict]:
        all_products = []
        print(f"🕷️  {self.site_name} - Crawl delay: {self.crawl_delay}s (STRICT)")
        for category in self.categories:
            print(f"\n📁 {category['name']}")
            soup = self.fetch_page(f"{self.base_url}{category['url']}")
            if not soup: continue

            # Velog uses <li> elements for products
            for elem in soup.select('li'):
                try:
                    # Find link with product name
                    link = elem.select_one('a[href]')
                    if not link: continue

                    url = link.get('href', '')
                    if not url or url == '#': continue
                    if not url.startswith('http'): url = f"{self.base_url}{url}"

                    # Extract name from link text
                    name = link.get_text(strip=True)
                    if not name or len(name) < 3: continue

                    # Extract ID from URL or generate from name
                    id_match = re.search(r'/(\w+)/?$', url)
                    external_id = id_match.group(1) if id_match else name.replace(' ', '_')[:50]

                    # Find price - look for .price class or text with RSD
                    price_elem = elem.select_one('.price')
                    if price_elem:
                        price = self.parse_price(price_elem.get_text(strip=True))
                    else:
                        # Try to find price in text
                        text = elem.get_text()
                        price_match = re.search(r'([\d\s\.,]+)\s*RSD', text)
                        if price_match:
                            price = self.parse_price(price_match.group(1))
                        else:
                            continue

                    if not price: continue

                    # Extract image
                    img_elem = elem.select_one('img')
                    image_url = ''
                    if img_elem:
                        img_src = img_elem.get('src', '') or img_elem.get('data-src', '')
                        if img_src:
                            image_url = f"{self.base_url}{img_src}" if not img_src.startswith('http') else img_src

                    all_products.append({
                        'external_id': external_id,
                        'name': name,
                        'category': category['name'],
                        'description': '',
                        'current_price': price,
                        'on_sale': False,
                        'sale_price': None,
                        'original_price': None,
                        'product_url': url,
                        'image_url': image_url,
                        'in_stock': True
                    })
                    print(f"   ✅ {all_products[-1]['name'][:40]:<40} - {price} RSD")
                except Exception as e:
                    pass  # Skip invalid items silently
        print(f"\n📊 Total: {len(all_products)}")
        return all_products
