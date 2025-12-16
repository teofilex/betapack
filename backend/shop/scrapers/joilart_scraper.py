"""
Scraper for JoilArt.com
"""
from typing import List, Dict
from .base import BaseScraper
import re


class JoilArtScraper(BaseScraper):
    """
    Scraper for https://joilart.com/

    Site structure:
    - Products are organized in categories
    - Each product has: name, price, dimensions, image
    - URL pattern: /proizvod/{ID}_{name}/show
    """

    def __init__(self):
        config = {
            'name': 'JoilArt',
            'url': 'https://joilart.com',
            'delay': 10  # 10 seconds between requests (respect strictest robots.txt)
        }
        super().__init__(config)

        # Kategorije koje ćemo scrape-ovati
        self.categories = [
            {'name': 'Kovani vrhovi i šiljci', 'url': '/proizvodi/1_kovani-elementi/1_kovani-vrhovi-i-siljci'},
            {'name': 'Cvetovi i listovi', 'url': '/proizvodi/1_kovani-elementi/41_cvetovi-i-listovi'},
            {'name': 'Basketi i kugle', 'url': '/proizvodi/1_kovani-elementi/42_basketi-kovanice-i-kugle'},
            {'name': 'Flah gladak', 'url': '/proizvod/3_flah-gladak/materijal'},
            {'name': 'Kutija kvadratna', 'url': '/proizvod/5_kutija-kvadratna-glatka/materijal'},
        ]

    def scrape_products(self) -> List[Dict]:
        """
        Scrape products from JoilArt.com
        """
        all_products = []

        print(f"🕷️  Starting scrape of {self.site_name}...")
        print(f"⏱️  Crawl delay: {self.crawl_delay}s between requests")
        print(f"📂 Scraping {len(self.categories)} categories...")

        for category in self.categories:
            print(f"\n📁 Category: {category['name']}")

            # Fetch category page
            category_url = f"{self.base_url}{category['url']}"
            soup = self.fetch_page(category_url)

            if not soup:
                print(f"⚠️  Failed to fetch {category['name']}")
                continue

            # Find all products on the page
            product_wrappers = soup.select('.product-wrapper')
            print(f"   Found {len(product_wrappers)} products")

            for wrapper in product_wrappers:
                try:
                    product = self._extract_product_data(wrapper, category['name'])
                    if product:
                        all_products.append(product)
                        status_icon = "🔥" if product['on_sale'] else "✅"
                        print(f"   {status_icon} {product['name'][:40]:<40} - {product['current_price']} RSD")
                except Exception as e:
                    print(f"   ⚠️  Error extracting product: {e}")
                    continue

        print(f"\n📊 Total products scraped: {len(all_products)}")
        return all_products

    def _extract_product_data(self, wrapper, category_name: str) -> Dict:
        """
        Extract product data from a product wrapper element
        """
        # Extract product link and ID
        link_elem = wrapper.select_one('.product-img a') or wrapper.select_one('.product-content h5 a')
        if not link_elem:
            return None

        product_url = link_elem.get('href', '')
        if not product_url.startswith('http'):
            product_url = f"{self.base_url}{product_url}"

        # Extract ID from URL (pattern: /proizvod/ID_name/show)
        id_match = re.search(r'/proizvod/(\d+)_', product_url)
        if not id_match:
            # Try alternative ID extraction
            id_match = re.search(r'/(\d+)_', product_url)

        external_id = id_match.group(1) if id_match else product_url.split('/')[-2]

        # Extract product name
        name_elem = wrapper.select_one('.product-content h5 a')
        name = name_elem.get_text(strip=True) if name_elem else 'Unknown'

        # Extract description (dimensions)
        description_elems = wrapper.select('.product-content h5')
        description_parts = []
        for elem in description_elems[1:]:  # Skip first h5 (that's the name)
            text = elem.get_text(strip=True)
            if text and 'RSD' not in text:
                description_parts.append(text)
        description = ', '.join(description_parts) if description_parts else ''

        # Extract price
        price_elem = wrapper.select_one('.product-content span')
        price_text = price_elem.get_text(strip=True) if price_elem else ''
        current_price = self.parse_price(price_text)

        if not current_price:
            return None

        # Check if on sale (has .akcija class)
        on_sale = wrapper.select_one('.akcija') is not None

        # Extract image
        img_elem = wrapper.select_one('.product-img img')
        image_url = ''
        if img_elem:
            img_src = img_elem.get('src', '')
            if img_src:
                image_url = f"{self.base_url}/{img_src}" if not img_src.startswith('http') else img_src

        return {
            'external_id': external_id,
            'name': name,
            'category': category_name,
            'description': description,
            'current_price': current_price,
            'on_sale': on_sale,
            'sale_price': current_price if on_sale else None,
            'original_price': None,  # JoilArt doesn't show original price
            'product_url': product_url,
            'image_url': image_url,
            'in_stock': True  # Assume all products are in stock (site doesn't show stock status)
        }
