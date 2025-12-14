# Instrukcije za reset baze podataka

Baza podataka je resetovana. Sada treba da pokrenete migracije.

## Koraci:

1. Instalirajte potrebne pakete (ako nisu instalirani):
   ```bash
   pip install -r requirements.txt
   ```

2. Pokrenite migracije:
   ```bash
   python manage.py migrate
   ```

3. (Opciono) Kreirajte superuser-a:
   ```bash
   python manage.py createsuperuser
   ```

4. (Opciono) Popunite bazu sa početnim podacima:
   ```bash
   python manage.py populate_db
   ```

## Šta je urađeno:

- ✅ Obrisana stara baza podataka (db.sqlite3)
- ✅ Obrisane stare migracije
- ✅ Kreirana nova početna migracija (0001_initial.py) koja uključuje:
  - Sva polja iz modela
  - Novo polje `sold_by_length` u Product modelu
  - `quantity` u OrderItem je sada DecimalField (podržava decimalne vrednosti za proizvode po metraži)

## Napomena:

Nova migracija uključuje sve izmene, uključujući podršku za proizvode koji se prodaju po metraži.



