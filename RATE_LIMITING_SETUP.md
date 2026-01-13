# Rate Limiting - Implementacija

## 📋 Šta je urađeno

Implementiran je **rate limiting** (ograničenje broja zahteva) za zaštitu API-ja od zloupotrebe.

### Dodati limiti:

| Endpoint | Limit | Opis |
|----------|-------|------|
| **Contact forma** | 3 poruke/sat | Sprečava spam poruke |
| **Kreiranje porudžbina** | 10 porudžbina/sat | Sprečava lažne porudžbine |
| **Anonimni korisnici** | 100 zahteva/sat | Opšti limit za sve ostale endpoint-e |
| **Ulogovani admini** | 1000 zahteva/sat | Admini imaju veći limit |

---

## 🔧 Tehnički detalji

### 1. Konfiguracija (`backend/backend/settings.py`)

Dodato u `REST_FRAMEWORK` konfiguraciju:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',      # Anonimni korisnici: 100 zahteva po satu
        'user': '1000/hour',     # Ulogovani admini: 1000 zahteva po satu
        'contact': '3/hour',     # Kontakt forma: 3 poruke po satu
        'orders': '10/hour',     # Porudžbine: 10 po satu
    }
}
```

### 2. Custom Throttle klase (`backend/shop/views.py`)

```python
# Custom throttle classes za specifične endpoint-e
class ContactThrottle(AnonRateThrottle):
    """Rate limiting za kontakt formu - 3 poruke po satu"""
    rate = 'contact'


class OrderThrottle(AnonRateThrottle):
    """Rate limiting za kreiranje porudžbina - 10 porudžbina po satu"""
    rate = 'orders'
```

### 3. Primena na endpoint-e

**Contact forma:**
```python
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([ContactThrottle])
def contact_message(request):
    # ...
```

**Order creation:**
```python
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    throttle_classes = [OrderThrottle]
    # ...
```

---

## 🧪 Testiranje

### Opcija 1: Python test script

```bash
cd /home/teofilex/Projects/gvozdjara

# Prvo pokreni development server u jednom terminalu:
pipenv run python backend/manage.py runserver

# Zatim u drugom terminalu pokreni test:
python3 test_rate_limiting.py
```

### Opcija 2: Bash script (jednostavniji)

```bash
cd /home/teofilex/Projects/gvozdjara

# Pokreni development server
pipenv run python backend/manage.py runserver

# U drugom terminalu:
./test_rate_limit_simple.sh
```

### Opcija 3: Manualno sa curl

```bash
# Pošalji 4 zahteva - 4. bi trebao da bude blokiran
for i in {1..4}; do
    curl -X POST http://localhost:8000/api/contact/ \
        -H "Content-Type: application/json" \
        -d '{"name":"Test","email":"test@test.com","phone":"0641234567","message":"Test"}' \
        -w "\nHTTP: %{http_code}\n"
    echo "---"
done
```

**Očekivani rezultat:**
- Prva 3 zahteva: `HTTP 201 Created` ✅
- Četvrti zahtev: `HTTP 429 Too Many Requests` 🚫

---

## 📊 Šta se dešava kada je limit prekoračen?

Kada korisnik pošalje previše zahteva, dobija odgovor:

```json
HTTP 429 Too Many Requests

{
  "detail": "Request was throttled. Expected available in 3421 seconds."
}
```

- **429** = HTTP kod za "Too Many Requests"
- Poruka kaže koliko sekundi korisnik mora da čeka pre sledećeg zahteva

---

## ⚙️ Kako Django prati zahteve?

Django REST Framework koristi **cache** za praćenje zahteva:

1. **Development (DEBUG=True):**
   - Koristi `LocMemCache` (u memoriji Python procesa)
   - Resetuje se kada restartuje server
   - Svaki proces ima svoj cache

2. **Production (DEBUG=False):**
   - Preporučeno: Redis cache za deljenje između procesa
   - Ili Memcached

### Kako dodati Redis za produkciju (opciono):

1. Instaliraj Redis:
```bash
pip install redis django-redis
```

2. U `settings.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

---

## 🎯 Best Practices

### 1. Različiti limiti za različite endpoint-e

- **Javni podaci** (products, categories): Viši limit (100/sat)
- **Forme** (contact, checkout): Niži limit (3-10/sat)
- **Admin panel**: Najviši limit (1000/sat)

### 2. Rate limiting po IP adresi

Django automatski prati zahteve po IP adresi za anonimne korisnike.

### 3. Whitelist za interne servise

Ako imaš mobilnu aplikaciju ili drugi servis koji poziva API:

```python
class CustomThrottle(AnonRateThrottle):
    def allow_request(self, request, view):
        # Whitelisted IPs nemaju rate limit
        if request.META.get('REMOTE_ADDR') in ['10.0.0.1', '192.168.1.100']:
            return True
        return super().allow_request(request, view)
```

### 4. Monitoring

Dodaj logging kada neko bude rate limited:

```python
import logging
logger = logging.getLogger(__name__)

# U throttle klasi:
def throttle_failure(self):
    logger.warning(f"Rate limit exceeded for IP: {self.get_ident()}")
```

---

## 🚀 Deployment

**Railway (production):**
- Rate limiting automatski radi ✅
- Koristi default cache (LocMemCache)
- Za veći saobraćaj, dodaj Redis na Railway

**Za Redis na Railway:**
1. Dodaj Redis plugin u Railway
2. Railway će automatski postaviti `REDIS_URL` env var
3. Dodaj `redis` i `django-redis` u `requirements.txt`
4. Update `settings.py` sa Redis cache konfigom

---

## 📝 Napomene

- **Ne utiče na performanse** - DRF throttling je vrlo efikasan
- **Reset limita** - Limiti se resetuju svaki sat (rolling window)
- **Development vs Production** - U development-u cache je u memoriji, resetuje se sa server restart-om
- **IP tracking** - Radi i za localhost (127.0.0.1) u testiranju

---

## ⚡ Brza provera da li radi

```bash
# Pošalji 5 zahteva brzo
for i in {1..5}; do
    curl -s -o /dev/null -w "%{http_code} " http://localhost:8000/api/contact/ \
        -X POST -H "Content-Type: application/json" \
        -d '{"name":"T","email":"t@t.com","phone":"0641234567","message":"Hi"}'
done
echo ""
```

**Očekivano:** `201 201 201 429 429` (prva 3 uspešna, 4. i 5. blokirani)

---

## 🔒 Sigurnost

Rate limiting štiti od:

✅ **Spam** - Neko ne može slati 1000 kontakt poruka
✅ **Brute force** - Ograničava pokušaje pogađanja passworda
✅ **DDoS** - Otežava preopterećenje servera
✅ **Scraping** - Otežava automatsko preuzimanje podataka
✅ **Fake orders** - Sprečava masovno kreiranje lažnih porudžbina

---

**Autor:** Claude Code (AI)
**Datum:** 2026-01-13
**Vreme implementacije:** 10 minuta
