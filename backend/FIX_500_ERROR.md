# Rešavanje greške 500 - Proizvodi ne mogu da se dodaju

## Problem
Greška 500 kada se pokušava da se doda proizvod ili kada se čitaju proizvodi. Verovatno je problem što baza nije ažurirana sa novim poljem `length_per_unit`.

## Rešenje

### 1. Proverite da li je migracija pokrenuta

```bash
cd backend
python manage.py showmigrations shop
```

Ako vidite `[ ] 0001_initial`, migracija nije pokrenuta.

### 2. Pokrenite migracije

```bash
python manage.py migrate
```

### 3. Ako migracija ne radi, resetujte bazu

**UPOZORENJE: Ovo će obrisati sve podatke!**

```bash
# Obrišite bazu
rm db.sqlite3  # ili del db.sqlite3 na Windows

# Pokrenite migracije ponovo
python manage.py migrate

# (Opciono) Popunite bazu sa početnim podacima
python manage.py populate_db
```

### 4. Ako i dalje ne radi, proverite da li postoje proizvodi bez length_per_unit

Ako imate postojeće proizvode u bazi koji su kreirani pre dodavanja `length_per_unit` polja, možda treba da ažurirate njihove vrednosti:

```python
# U Django shell-u (python manage.py shell)
from shop.models import Product
from decimal import Decimal

# Ažuriraj sve proizvode koji nemaju length_per_unit
Product.objects.filter(length_per_unit__isnull=True).update(length_per_unit=Decimal('6.0'))
# ili
for product in Product.objects.all():
    if not product.length_per_unit or product.length_per_unit == 0:
        product.length_per_unit = 6.0
        product.save()
```

## Šta je urađeno

1. ✅ Dodato `length_per_unit` polje u Product model sa default=6.0
2. ✅ Ažuriran serializer da osigura da `length_per_unit` uvek ima vrednost
3. ✅ Dodata zaštita u modelu (`save` metoda) da osigura default vrednost
4. ✅ Dodata zaštita u serializeru (`to_representation`) da osigura da se uvek vraća vrednost

## Provera

Nakon pokretanja migracija, proverite:

```bash
python manage.py shell
```

```python
from shop.models import Product
# Proverite da li svi proizvodi imaju length_per_unit
for p in Product.objects.all():
    print(f"{p.name}: length_per_unit = {p.length_per_unit}")
```



