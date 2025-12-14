# Reset baze i setup instrukcije

## Urađeno:
1. ✅ Obrisana baza podataka (db.sqlite3)
2. ✅ Obrisane sve migracije (osim __init__.py)
3. ✅ Kreirana nova početna migracija sa svim modelima

## Sledeći koraci:

### 1. Pokrenite migracije
```bash
cd backend
python manage.py migrate
```

### 2. Kreirajte superuser-a
```bash
python manage.py createsuperuser
```

Unesite:
- Username: admin (ili željeno ime)
- Email: (opciono)
- Password: (unosite 2 puta)

### 3. (Opciono) Popunite bazu sa početnim podacima
```bash
python manage.py populate_db
```

## Napomena:
- Sve kategorije, podkategorije i proizvodi su obrisani
- Superuser će biti kreiran ručno
- Baza je sada čista i spremna za rad



