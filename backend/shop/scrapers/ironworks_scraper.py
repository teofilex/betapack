"""
Scraper for IronWorks.rs
"""
from typing import List, Dict
from .base import BaseScraper
import re

class IronWorksScraper(BaseScraper):
    def __init__(self):
        config = {'name': 'IronWorks', 'url': 'https://ironworks.rs', 'delay': 10}
        super().__init__(config)
        self.categories = [
            {'name': 'Šiljci', 'url': '/kategorija/siljci/'},
            {'name': 'Sklopovi', 'url': '/kategorija/sklopovi/'},
            {'name': 'Grifovani flah', 'url': '/kategorija/grifovani-flah/'},
            {'name': 'Grifovani firiket', 'url': '/kategorija/grifovani-firiket/'},
            {'name': 'Kvadratne, pravougaone i okrugle cevi', 'url': '/kategorija/ravne-kutije/'},
            {'name': 'Kugle i poklopci', 'url': '/kategorija/kugle-i-poklopci/'},
            {'name': 'Ravni firiket', 'url': '/kategorija/ravan-firiket-okrugli-valjani-celik/'},
            {'name': 'Asimetrični S elementi', 'url': '/kategorija/asimetricni-s-elementi/'},
            {'name': 'Simetrični S elementi', 'url': '/kategorija/simetricni-s-elementi/'},
            {'name': 'Grifovane kutije', 'url': '/kategorija/grifovane-kutije/'},
            {'name': 'Rozetne', 'url': '/kategorija/rozetne/'},
            {'name': 'Basketi', 'url': '/kategorija/basketi/'},
            {'name': 'Anker ploče', 'url': '/kategorija/anker-ploce/'},
            {'name': 'Asimetrične perece', 'url': '/kategorija/asimetricne-perece/'},
            {'name': 'Cvetovi i listovi', 'url': '/kategorija/cvetovi-i-listovi/'},
            {'name': 'Dekorativni limovi', 'url': '/kategorija/dekorativni-i-ostali-limovi/'},
            {'name': 'Ispune i polja', 'url': '/kategorija/ispune-polja-i-upredene/'},
            {'name': 'Krugovi i elipse', 'url': '/kategorija/krugovi-i-elipse/'},
            {'name': 'Odkivci i kovanice', 'url': '/kategorija/odkivci-kovanice/'},
            {'name': 'Okrugle šavne cevi', 'url': '/kategorija/okrugle-savne-cevi/'},
            {'name': 'Prstenovi i obojnice', 'url': '/kategorija/prstenovi-obojnice/'},
            {'name': 'Ravni flahovi i L profili', 'url': '/kategorija/ravni-flahovi-i-l-profili/'},
            {'name': 'Rukohvati i završetci', 'url': '/kategorija/rukohvati-i-zavrseci-rukohvata/'},
            {'name': 'Šildovi i kvake', 'url': '/kategorija/sildovi-kvake-i-sarke/'},
            {'name': 'Simetrične perece', 'url': '/kategorija/simetricne-perece/'},
            {'name': 'Panelne ograde', 'url': '/kategorija/panelne-ograde/'},
        ]

    def scrape_products(self) -> List[Dict]:
        all_products = []
        print(f"🕷️  {self.site_name} - Crawl delay: {self.crawl_delay}s")
        for category in self.categories:
            print(f"\n📁 {category['name']}")
            soup = self.fetch_page(f"{self.base_url}{category['url']}")
            if not soup: continue
            for elem in soup.select('.product, .item, article'):
                try:
                    link = elem.select_one('a')
                    if not link: continue
                    url = link.get('href', '')
                    if not url.startswith('http'): url = f"{self.base_url}{url}"
                    id_match = re.search(r'/(\d+)', url)
                    name_elem = elem.select_one('h2, h3, .title')
                    price_elem = elem.select_one('.price, span')
                    price = self.parse_price(price_elem.get_text(strip=True) if price_elem else '')
                    if not price: continue
                    all_products.append({
                        'external_id': id_match.group(1) if id_match else url.split('/')[-1],
                        'name': name_elem.get_text(strip=True) if name_elem else 'Unknown',
                        'category': category['name'],
                        'description': '',
                        'current_price': price,
                        'on_sale': False,
                        'sale_price': None,
                        'original_price': None,
                        'product_url': url,
                        'image_url': (elem.select_one('img').get('src', '') if elem.select_one('img') else ''),
                        'in_stock': True
                    })
                    print(f"   ✅ {all_products[-1]['name'][:40]:<40} - {price} RSD")
                except Exception as e: print(f"   ⚠️  {e}")
        print(f"\n📊 Total: {len(all_products)}")
        return all_products
