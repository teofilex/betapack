# Brzo rešenje za grešku "no such column: shop_product.length_per_unit"

## Problem
Baza nema kolonu `length_per_unit` u tabeli `shop_product`, što uzrokuje grešku 500.

## Rešenje 1: Pokrenite SQL skriptu (NAJBRŽE)

```bash
cd backend
python add_length_per_unit_column.py
```

Ovo će direktno dodati kolonu u SQLite bazu.

## Rešenje 2: Pokrenite migracije

```bash
cd backend
python manage.py migrate shop
```

Ako dobijete grešku da migracija već postoji, pokrenite:

```bash
python manage.py migrate shop 0014 --fake
python manage.py migrate shop
```

## Rešenje 3: Reset baze (ako ništa drugo ne radi)

**UPOZORENJE: Ovo će obrisati sve podatke!**

```bash
cd backend
rm db.sqlite3  # ili del db.sqlite3 na Windows
python manage.py migrate
python manage.py createsuperuser
```

## Provera

Nakon pokretanja skripte ili migracija, proverite:

```bash
python manage.py shell
```

```python
from shop.models import Product
# Proverite da li svi proizvodi imaju length_per_unit
for p in Product.objects.all():
    print(f"{p.name}: length_per_unit = {p.length_per_unit}")
```



