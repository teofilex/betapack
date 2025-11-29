# 🔨 Bravarska Radnja - Web Aplikacija

Moderna web aplikacija za bravarsku radnju sa katalogom proizvoda, sistemom za narudžbine i admin panelom.

## 📋 Sadržaj

- Django backend API
- Vue.js 3 frontend (Korisničke stranice + Admin panel)
- Proizvodi sa varijantama (dimenzije) i galerijom slika
- Sistem za narudžbine sa email notifikacijama
- Responzivan moderan dizajn

---

## 🚀 Kako pokrenuti projekat

### 1. Backend (Django)

```bash
cd backend

# Instalacija zavisnosti
pipenv install

# Kreiranje migracija (ako je potrebno)
pipenv run python manage.py makemigrations
pipenv run python manage.py migrate

# Kreiranje superuser naloga
pipenv run python manage.py createsuperuser

# Pokretanje servera
pipenv run python manage.py runserver
```

Backend će biti dostupan na: `http://localhost:8000`

Django admin panel: `http://localhost:8000/admin`

### 2. Frontend (Vue.js)

```bash
cd frontend

# Instalacija zavisnosti
npm install

# Pokretanje development servera
npm run dev
```

Frontend će biti dostupan na: `http://localhost:5173`

---

## 🎯 Funkcionalnosti

### 👤 Korisničke stranice

#### 🏠 **Početna / Prodavnica** (`/`)
- Hero sekcija
- Izdvojeni proizvodi (featured)
- Kompletan katalog sa filterima
- Akcijske cene (precrtana stara, prikazana nova)
- Responsive grid layout
- Pretraga proizvoda
- Filtriranje po kategorijama
- Prikaz samo proizvoda na akciji

#### 📦 **Detalji proizvoda** (`/proizvod/:id`)
- Galerija slika sa thumbnail pregledом
- Selekcija varijanti/dimenzija
- Izbor količine
- Prikaz akcijske cene
- Dodavanje u korpu
- Stock status

#### 🛒 **Korpa** (`/cart`)
- Pregled proizvoda u korpi
- Ažuriranje količina
- Uklanjanje proizvoda
- Prikaz ukupnog iznosa
- Prelazak na checkout

#### ✅ **Checkout** (`/checkout`)
- Forma sa validacijom
- **Obavezan telefon** (validacija za srpske brojeve)
- Opcioni email
- Adresa dostave (opciono)
- Napomena
- Kreiranje narudžbine

#### 🎉 **Uspešna narudžbina** (`/order-success/:orderId`)
- Potvrda kreirane narudžbine
- Broj narudžbine
- Informacije o sledećim koracima
- Kontakt podaci

#### 📞 **Kontakt** (`/kontakt`)
- Kontakt forma
- Click-to-call dugmad
- Google Maps integracija
- Radno vreme

#### ℹ️ **O nama** (`/o-nama`)
- Informacije o kompaniji
- Vrednosti i prednosti
- Lista proizvoda i usluga
- CTA sekcija

---

### 🔐 Admin Panel (`/admin/panel`)

#### Funkcionalnosti:
- ✅ **Kategorije** - Upravljanje kategorijama proizvoda
- ✅ **Potkategorije** - Organizacija potkategorija
- ✅ **Proizvodi** - CRUD operacije
  - Dodavanje varijanti (dimenzije)
  - Upload višestrukih slika
  - Akcijske cene
  - Featured proizvodi
  - Stock management
- ✅ **Narudžbine** - Pregled i upravljanje
  - Detaljan prikaz narudžbine
  - Ažuriranje statusa
  - Kontakt informacije kupca
  - Click-to-call

---

## 🗄️ Backend API Endpoints

### Javni (bez autentifikacije):
- `GET /api/categories/` - Lista kategorija
- `GET /api/subcategories/` - Lista potkategorija
- `GET /api/products/` - Lista proizvoda (sa variants i images)
- `GET /api/products/{id}/` - Detalji proizvoda
- `GET /api/product-variants/` - Lista varijanti
- `GET /api/product-images/` - Liste slika
- `POST /api/orders/` - Kreiranje narudžbine

### Samo admin (JWT token):
- `POST/PUT/DELETE /api/categories/` - CRUD kategorija
- `POST/PUT/DELETE /api/subcategories/` - CRUD potkategorija
- `POST/PUT/DELETE /api/products/` - CRUD proizvoda
- `POST/PUT/DELETE /api/product-variants/` - CRUD varijanti
- `POST/PUT/DELETE /api/product-images/` - CRUD slika
- `GET /api/orders/` - Pregled narudžbina
- `POST /api/orders/{id}/update_status/` - Ažuriranje statusa

---

## 📊 Baza podataka - Modeli

### Product (Proizvod)
- name, description, price
- category, subcategory
- on_sale, sale_price
- featured, in_stock, stock_quantity
- **Relacije:** variants (1:N), images (1:N)

### ProductVariant (Varijanta)
- name (npr. "180×135×18mm")
- price_adjustment (+/- od osnovne cene)
- sku, in_stock, stock_quantity

### ProductImage (Slika)
- image (upload)
- is_primary, order, alt_text

### Order (Narudžbina)
- customer_name
- **customer_phone** (obavezan, validiran)
- customer_email (opciono)
- delivery_address, notes
- status (pending, confirmed, processing, completed, cancelled)
- total_amount
- sms_sent, email_sent

### OrderItem (Stavka narudžbine)
- product, variant (opciono)
- quantity, unit_price, total_price
- product_name, variant_name (snapshot)

---

## 🎨 Dizajn

### Boje:
- **Primary:** Orange (#f97316) - CTA dugmad, akcenti
- **Dark:** Gray-900 (#111827) - Header, footer, tekst
- **Background:** Gray-50 (#f9fafb)
- **Success:** Green-700 - Cene
- **Error:** Red-600 - Sale badge, upozorenja

### Tipografija:
- Font: System fonts (sans-serif)
- Headings: Bold, velika veličina
- Body: Regular, dobra čitljivost

### Komponente:
- Zaobljeni uglovi (rounded-xl)
- Hover efekti i transitions
- Shadow-lg za kartice
- Sticky navigacija

---

## 📧 Email Notifikacije

### Kada se kreira narudžbina:
1. **Vlasniku** se šalje email sa:
   - Broj narudžbine
   - Podaci kupca (ime, telefon, email)
   - Lista proizvoda sa količinama i cenama
   - Ukupan iznos
   - Napomena kupca

2. **Korisniku** (planiran SMS):
   - Potvrda narudžbine
   - Broj za kontakt

---

## ⚙️ Konfiguracija

### Email (backend/backend/settings.py):
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # TODO: env varijabla
EMAIL_HOST_PASSWORD = 'your-password'  # TODO: env varijabla
DEFAULT_FROM_EMAIL = 'Bravarska Radnja <noreply@gvozdjara.rs>'
```

### CORS (backend/backend/settings.py):
```python
# Development - hardkodovani localhost domovi
if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",  # Vue dev server
        "http://localhost:8080",
    ]
else:
    # Production - čita iz environment varijable
    # Format: CORS_ALLOWED_ORIGINS=https://domain1.com,https://domain2.com
    # Ako nije postavljena, automatski generiše iz ALLOWED_HOSTS
```

**Za produkciju**, postavi environment varijablu:
```bash
CORS_ALLOWED_ORIGINS=https://tvoj-domen.com,https://www.tvoj-domen.com,https://betapack.vercel.app
```

---

## 📂 Struktura projekta

```
gvozdjara/
├── backend/                 # Django backend
│   ├── backend/
│   │   ├── settings.py     # Konfiguracija
│   │   └── urls.py         # URL routing
│   ├── shop/               # Glavna aplikacija
│   │   ├── models.py       # Baza podataka modeli
│   │   ├── serializers.py  # DRF serializeri
│   │   ├── views.py        # API view-ovi
│   │   └── admin.py        # Django admin
│   ├── media/              # Uploadovane slike
│   └── manage.py
│
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── components/     # Deljene komponente
│   │   │   ├── TheHeader.vue
│   │   │   └── TheFooter.vue
│   │   ├── pages/
│   │   │   ├── user/       # Korisničke stranice
│   │   │   │   ├── ShopView.vue
│   │   │   │   ├── ProductDetailView.vue
│   │   │   │   ├── CartView.vue
│   │   │   │   ├── CheckoutView.vue
│   │   │   │   ├── OrderSuccessView.vue
│   │   │   │   ├── ContactView.vue
│   │   │   │   └── AboutView.vue
│   │   │   └── admin/      # Admin panel
│   │   ├── admin/
│   │   │   ├── components/
│   │   │   │   ├── ProductManager.vue
│   │   │   │   ├── ProductImageManager.vue
│   │   │   │   ├── ProductVariantManager.vue
│   │   │   │   ├── ProductDetailModal.vue
│   │   │   │   ├── OrdersManager.vue
│   │   │   │   ├── CategoryManager.vue
│   │   │   │   └── SubcategoryManager.vue
│   │   │   └── pages/
│   │   │       ├── Login.vue
│   │   │       └── AdminView.vue
│   │   ├── store/          # Pinia stores
│   │   │   ├── auth.js
│   │   │   ├── cart.js
│   │   │   ├── products.js
│   │   │   └── categories.js
│   │   └── router/         # Vue Router
│   │       └── index.js
│   └── package.json
│
└── README.md
```

---

## 🔐 Pristup admin panelu

1. Kreiraj superuser:
```bash
cd backend
pipenv run python manage.py createsuperuser
```

2. Otvori: `http://localhost:5173/admin/login`

3. Unesi kredencijale

---

## 📝 TODO (Buduća poboljšanja)

- [ ] SMS integracija (Twilio ili lokalni gateway)
- [ ] Export narudžbina u PDF/Excel
- [ ] Izveštaji i statistika prodaje
- [ ] Naprednije filtriranje proizvoda
- [ ] Wishlist funkcionalnost
- [ ] Product reviews/ratings
- [ ] Multi-language podrška
- [ ] SEO optimizacije
- [ ] PWA funkcionalnosti

---

## 📞 Kontakt informacije

**Beta Pack d.o.o.**
Pukovnika Milenka Pavlovića 159 A, Zemun-Batajnica

Telefon: 065/330 02 42 | 063/8757 725
Email: office@betapack.co.rs

---

## 📄 Licenca

Privatni projekat za bravarsku radnju.

---

**Napravljeno sa ❤️ koristeći Django + Vue.js + TailwindCSS**
