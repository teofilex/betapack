# 🕷️ Scraping Sistem - Primer Korišćenja

## Šta je implementirano

### 1. **Django Modeli** ✅
- `CompetitorSite` - Konkurentski sajtovi za praćenje
- `ScrapedProduct` - Proizvodi scraped sa konkurentskih sajtova
- `PriceHistory` - Istorija promena cena
- `ScrapeLog` - Logovi scraping operacija

### 2. **Base Scraper** ✅
- Automatski respektuje `crawl-delay`
- Realistični browser headers (ne izgleda kao bot)
- Parse cene (SR i US format: 1.200,00 ili 1,200.00)
- Error handling i timeout

### 3. **JoilArt Scraper** ✅ (Primer)
- Šablon za scraping JoilArt.com
- Treba prilagoditi HTML selektore (site-specific)

### 4. **Django Management Command** ✅
```bash
python manage.py scrape_competitors
python manage.py scrape_competitors --site joilart
python manage.py scrape_competitors --force
```

### 5. **Admin Panel** ✅
- Pregled svih scraped proizvoda
- Filteri po sajtu, kategoriji, akcijama
- Istorija cena za svaki proizvod

---

## Kako pokrećeš scraping?

### **Korak 1: Dodaj konkurentski sajt u bazu**

Idi u Django Admin → Competitor Sites → Add

```
Name: JoilArt
URL: https://joilart.com
Is Active: ✓
Scrape Interval Hours: 24
Crawl Delay Seconds: 3
```

### **Korak 2: Pokreni scraping**

```bash
cd backend
pipenv run python manage.py scrape_competitors
```

**Izlaz:**
```
🕷️  Scraping JoilArt...
⏱️  Crawl delay: 3s
✅ Scraped: Tačka 70 - 1200.00 RSD
📊 Total products scraped: 15
✅ JoilArt: Found 15, New: 10, Updated: 5
```

### **Korak 3: Proveri rezultate u Admin panelu**

Django Admin → Scraped Products

| Sajt | Proizvod | Kategorija | Cena | Na akciji | Poslednji update |
|------|----------|------------|------|-----------|------------------|
| JoilArt | Tačka 70 - 180x135 | Kovani elementi | 1.200 RSD | ❌ | 16.12.2025 |
| JoilArt | Profil 40x40 | Profili | 850 RSD | ✅ (-15%) | 16.12.2025 |

---

## Kako dodaš novi sajt za scraping?

### **Primer: Dodavanje Jeep Commerce scrapcera**

**1. Kreiraj `jeepcommerce_scraper.py`:**

```python
from typing import List, Dict
from .base import BaseScraper

class JeepCommerceScraper(BaseScraper):
    def __init__(self):
        config = {
            'name': 'JeepCommerce',
            'url': 'https://jeepcommerce.rs',
            'delay': 3
        }
        super().__init__(config)

    def scrape_products(self) -> List[Dict]:
        products = []

        # 1. Fetch category page
        soup = self.fetch_page(f"{self.base_url}/shop")

        # 2. Find all product links
        product_links = soup.select('.product-item a')  # Inspect HTML to find selector

        # 3. Loop through products
        for link in product_links:
            product_url = link['href']
            product_soup = self.fetch_page(product_url)

            # Extract data
            name = product_soup.select_one('.product-title').text.strip()
            price_text = product_soup.select_one('.price').text
            price = self.parse_price(price_text)

            products.append({
                'external_id': product_url.split('/')[-1],
                'name': name,
                'category': 'Cevi',
                'current_price': price,
                'product_url': product_url,
                'in_stock': True
            })

        return products
```

**2. Registruj u management command:**

```python
# shop/management/commands/scrape_competitors.py

def get_scraper(self, site_name: str):
    scrapers = {
        'joilart': JoilArtScraper,
        'jeepcommerce': JeepCommerceScraper,  # ← Dodaj ovde
    }
    ...
```

**3. Dodaj sajt u Admin panel i pokreni:**

```bash
python manage.py scrape_competitors --site jeepcommerce
```

---

## Automatsko scraping sa Celery (opciono)

Ako želiš automatski daily scraping bez ručnog pokretanja:

### **1. Instaluj Celery + Redis:**

```bash
pipenv install celery redis
```

### **2. Kreiraj `celery.py`:**

```python
# backend/celery.py
from celery import Celery
from celery.schedules import crontab

app = Celery('backend')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'scrape-competitors-daily': {
        'task': 'shop.tasks.scrape_all_competitors',
        'schedule': crontab(hour=2, minute=0),  # Every day at 2:00 AM
    },
}
```

### **3. Kreiraj `tasks.py`:**

```python
# shop/tasks.py
from celery import shared_task
from django.core.management import call_command

@shared_task
def scrape_all_competitors():
    call_command('scrape_competitors')
```

### **4. Pokreni Celery worker:**

```bash
celery -A backend worker -l info
celery -A backend beat -l info
```

---

## Šta dalje?

### **Faza 1: Testiranje (SADA)** ✅
- [x] Modeli kreirani
- [x] Base scraper
- [x] Primer JoilArt scraper
- [x] Management command
- [x] Admin panel

### **Faza 2: Implementacija pravih scraper-a (2-3 dana)**
- [ ] Inspektovati HTML strukturu svakog sajta
- [ ] Implementirati scraper za JoilArt (pravi selektori)
- [ ] Implementirati scraper za Jeep Commerce
- [ ] Implementirati scraper za Hanan
- [ ] Implementirati scraper za Velog
- [ ] Implementirati scraper za IronWorks

### **Faza 3: Vue Admin Panel Tab (1 dan)**
- [ ] API endpoint: `GET /api/competitors/products/`
- [ ] Vue component: `CompetitorProducts.vue`
- [ ] Tabela sa filterima (sajt, kategorija, akcije)
- [ ] Grafovi promena cena (Chart.js)

### **Faza 4: Automatizacija (opciono)**
- [ ] Celery + Redis setup
- [ ] Daily automatic scraping
- [ ] Email alerts za nove akcije

---

## Legalni aspekti - Podsetnik

✅ **Dozvoljeno:**
- Scraping javno dostupnih podataka
- Interno korišćenje za analizu konkurencije
- Respektovanje robots.txt i crawl-delay

❌ **Zabranjeno:**
- Redistribucija scraped podataka
- Opterećivanje servera (brzi request-ovi)
- Ignorisanje robots.txt

**Naš pristup:**
- ✅ 3-10s delay između request-ova
- ✅ Realistični browser User-Agent
- ✅ Respektujemo robots.txt
- ✅ Samo interno korišćenje

---

## Pitanja?

Da li želiš da nastavimo sa:
1. **Implementacijom pravih scraper-a** (2-3 dana)
2. **Vue admin panel tab prvo** (1 dan)
3. **Testiranje ovog MVP-a** (30min)

Reci mi šta ti odgovara!
