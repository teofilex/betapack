# 🚀 Quick Start: Email Notifikacije i Kontakt Forma

Ovaj dokument pokriva konfiguraciju email-ova za:
- ✉️ **Kontakt formu** - Prijem poruka od posetilaca
- 📦 **Notifikacije o porudžbinama** - Automatski email-ovi za nove porudžbine

---

## TL;DR - Brza konfiguracija (5 minuta)

### 1. Kreiraj Gmail App Password

1. Idi na: https://myaccount.google.com/apppasswords
2. Kreiraj novi App Password za "Mail"
3. Kopiraj 16-karakterni kod

### 2. Kreiraj `.env` fajl

```bash
cd backend
nano .env
```

Dodaj:

```env
# Email konfiguracija
EMAIL_HOST_USER=tvoj-gmail@gmail.com
EMAIL_HOST_PASSWORD=tvoj-app-password-16-karaktera

# Email primaoci
OWNER_EMAILS=office@betapack.co.rs
CONTACT_EMAIL_RECIPIENT=office@betapack.co.rs
```

Sačuvaj i zatvori (Ctrl+X, Y, Enter)

### 3. Restartuj backend

```bash
# Ugasi postojeći server (Ctrl+C) pa pokreni ponovo
pipenv run python manage.py runserver
```

### 4. Testiraj!

**Kontakt forma:**
- Idi na stranicu Kontakt
- Popuni formu i pošalji
- Proveri email inbox na `office@betapack.co.rs`

**Porudžbine:**
- Kreiraj test porudžbinu
- Proveri email inbox na `office@betapack.co.rs`

---

## Šta se dešava?

### Kontakt Forma
✅ Korisnik pošalje poruku → Email stiže vlasniku
✅ Poruka se čuva u bazi podataka
✅ Admin može videti sve poruke u panelu
✅ Možeš označiti poruke kao pročitane/odgovorene

### Porudžbine
✅ Kupac kreira porudžbinu → Email automatski stiže vlasniku
✅ Kupac vidi potvrdu na ekranu
✅ Vlasnik dobija svu info: ime, telefon, stavke, cenu
✅ Real-time notifikacija u admin panelu

---

## Alternativa: Test mod (bez Gmail-a)

Ako ne želiš da konfiguriš Gmail odmah, email će se ispisivati u konzoli:

U `backend/backend/settings.py` promeni liniju 163:

```python
# Umesto:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Koristi:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Restartuj server i svi email-ovi će se pojaviti u terminalu!

---

## Pregled Kontakt Poruka

Sve poruke sa kontakt forme se čuvaju u bazi i možeš ih videti u admin panelu:

1. Idi na: http://127.0.0.1:8000/admin/
2. Login
3. Klikni na **"Kontakt poruke"**
4. Vidiš: ime, telefon, email, poruku, status (pročitano/odgovoreno)

---

## Više informacija

Pogledaj: [EMAIL_SETUP.md](backend/EMAIL_SETUP.md) za detaljno uputstvo
