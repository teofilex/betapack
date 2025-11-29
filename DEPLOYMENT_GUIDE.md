# 🚀 Deployment Guide - Gvozdjara E-commerce

Ovaj vodič pokriva kompletno postavljanje aplikacije na production za besplatno testiranje.

## 📋 Pregled

Ovaj projekat koristi:
- **Backend:** Django REST Framework (Python)
- **Frontend:** Vue 3 + Vite
- **Database:** PostgreSQL (production) / SQLite (development)
- **Media Files:** Lokalni storage (development) / Cloudinary (production)

## 🎯 Preporučena arhitektura za deployment

### Opcija 1: Railway.app (Preporučeno)
- ✅ Besplatno za male projekte
- ✅ Automatski PostgreSQL
- ✅ Jednostavno postavljanje
- ✅ Continuous deployment sa GitHub

### Opcija 2: Render.com
- ✅ Besplatan tier
- ✅ PostgreSQL uključen
- ⚠️ Sporiji cold start

---

## 🔧 Priprema Backend-a

### 1. Verzije i zavisnosti

Backend je već pripremljen sa sledećim fajlovima:

- ✅ `requirements.txt` - Python zavisnosti
- ✅ `runtime.txt` - Python verzija (3.12.3)
- ✅ `Procfile` - Gunicorn web server konfiguracija
- ✅ `.env.production.example` - Template za production environment

### 2. Environment Variables za Backend

Potrebne environment varijable (postavi ih na Railway/Render):

```bash
# Django
SECRET_KEY=vaš-sigurni-tajni-ključ
DEBUG=False
ALLOWED_HOSTS=tvoj-domen.com,www.tvoj-domen.com

# Database (Railway/Render automatski postave DATABASE_URL)
DATABASE_URL=postgresql://...

# CORS (možeš dodati više domena odvojeno zarezom)
CORS_ALLOWED_ORIGINS=https://tvoj-frontend-domen.com,https://www.tvoj-frontend-domen.com,https://betapack.vercel.app

# CSRF Trusted Origins (opciono, ako treba dodatni domeni)
CSRF_TRUSTED_ORIGINS=https://tvoj-frontend-domen.com,https://www.tvoj-frontend-domen.com

# Email (Gmail sa App Password)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tvoj.email@gmail.com
EMAIL_HOST_PASSWORD=tvoj-app-password
DEFAULT_FROM_EMAIL=Bravarska Radnja <noreply@gvozdjara.rs>

# Email Recipients
OWNER_EMAILS=office@betapack.co.rs
CONTACT_EMAIL_RECIPIENT=office@betapack.co.rs
```

### 3. Generisanje SECRET_KEY

```bash
cd backend
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

---

## 🎨 Priprema Frontend-a

### 1. Environment Variables za Frontend

Kreiraj `.env.production` fajl u `frontend/` direktorijumu:

```bash
VITE_API_BASE_URL=https://tvoj-backend-domen.com/api
```

### 2. Build Frontend-a

```bash
cd frontend
npm install
npm run build
```

Ovo će kreirati `dist/` direktorijum sa production build-om.

---

## ☁️ Deployment na Railway.app

### Backend Deployment

1. **Napravi nalog na Railway.app**
   - Idi na https://railway.app
   - Registruj se sa GitHub nalogom

2. **Kreiraj novi projekat**
   - Klikni "New Project"
   - Izaberi "Deploy from GitHub repo"
   - Izaberi `gvozdjara` repozitorij

3. **Podesi Backend servis**
   - Klikni na kreiran servis
   - Idi na "Settings" tab
   - **Root Directory:** postavi na `backend`
   - **Start Command:** `gunicorn backend.wsgi --bind 0.0.0.0:$PORT`

4. **Dodaj PostgreSQL bazu**
   - U projektu klikni "+ New"
   - Izaberi "Database" → "PostgreSQL"
   - Railway će automatski kreirati `DATABASE_URL` varijablu

5. **Postavi Environment Variables**
   - U backend servisu idi na "Variables" tab
   - Dodaj sve potrebne varijable iz sekcije "Environment Variables za Backend"
   - `DATABASE_URL` je već automatski postavljen

6. **Deploy**
   - Railway će automatski deploy-ovati
   - Sačekaj da se build završi
   - Proveri logove da li ima grešaka

7. **Run Migrations**
   - U "Settings" → "Deploy" → dodaj Custom Start Command:
   ```bash
   python manage.py migrate && gunicorn backend.wsgi --bind 0.0.0.0:$PORT
   ```

8. **Kreiraj admin korisnika**
   - Koristi Railway CLI ili Web Shell:
   ```bash
   python manage.py createsuperuser
   ```

### Frontend Deployment

Opcije za frontend:

#### Opcija A: Vercel (Preporučeno za Vue)

1. Idi na https://vercel.com
2. "Import Project" → Izaberi GitHub repo
3. **Root Directory:** `frontend`
4. **Framework Preset:** Vite
5. **Environment Variables:**
   - Dodaj `VITE_API_BASE_URL` sa URL-om tvog Railway backend-a
6. Deploy!

#### Opcija B: Netlify

1. Idi na https://netlify.com
2. "Add new site" → "Import from Git"
3. Izaberi repo
4. **Base directory:** `frontend`
5. **Build command:** `npm run build`
6. **Publish directory:** `frontend/dist`
7. **Environment Variables:**
   - Dodaj `VITE_API_BASE_URL`
8. Deploy!

---

## 📸 Media Files - Cloudinary Setup

Za production, preporučuje se Cloudinary za čuvanje slika proizvoda.

### 1. Kreiraj Cloudinary nalog

- Idi na https://cloudinary.com
- Registruj se (besplatan tier)
- Kopiraj: Cloud Name, API Key, API Secret

### 2. Instaliraj Cloudinary package

```bash
cd backend
pipenv install django-cloudinary-storage cloudinary
pipenv requirements > requirements.txt
```

### 3. Update settings.py

Već je pripremljeno u `backend/settings.py` - samo uncomment Cloudinary sekciju:

```python
if not DEBUG:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api

    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET')
    )

    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

### 4. Dodaj Cloudinary Environment Variables

Na Railway/Render dodaj:

```bash
CLOUDINARY_CLOUD_NAME=tvoj-cloud-name
CLOUDINARY_API_KEY=tvoj-api-key
CLOUDINARY_API_SECRET=tvoj-api-secret
```

---

## ✅ Post-Deployment Checklist

Nakon deployment-a proveri:

- [ ] Backend je online i odgovara na `/api/` endpoint
- [ ] Frontend je online i učitava se
- [ ] Admin panel je dostupan
- [ ] Logovanje radi
- [ ] Proizvodi se učitavaju
- [ ] Slike proizvoda rade (Cloudinary)
- [ ] Kontakt forma šalje emailove
- [ ] Narudžbine se kreiraju
- [ ] Admin notifikacije za narudžbine rade

---

## 🐛 Troubleshooting

### Backend ne startuje

1. Proveri logove na Railway/Render
2. Proveri da li su sve environment varijable postavljene
3. Proveri `ALLOWED_HOSTS`

### Frontend ne može da pristupi backend-u

1. Proveri `VITE_API_BASE_URL` u frontend environment
2. Proveri `CORS_ALLOWED_ORIGINS` u backend environment
3. Proveri da li backend URL ima `/api` na kraju

### Slike se ne učitavaju

1. Proveri da li je Cloudinary ispravno konfigurisan
2. Proveri environment varijable za Cloudinary
3. U development mode, slike se čuvaju lokalno u `media/`

### Emailovi se ne šalju

1. Proveri Gmail App Password
2. Proveri `EMAIL_HOST_USER` i `EMAIL_HOST_PASSWORD`
3. Proveri da li je `DEBUG=False` (prodcution koristi SMTP, dev koristi console)

---

## 📞 Dodatna Pomoć

Za dodatna pitanja ili probleme:
- Railway docs: https://docs.railway.app/
- Render docs: https://render.com/docs
- Cloudinary docs: https://cloudinary.com/documentation

---

## 🔒 Sigurnost

**VAŽNO za production:**

1. ✅ Postavi `DEBUG=False`
2. ✅ Koristi jaki `SECRET_KEY`
3. ✅ Nikada ne commit-uj `.env` fajlove
4. ✅ Koristi App Password za Gmail (ne glavnu lozinku)
5. ✅ Postavi ispravne `ALLOWED_HOSTS` i `CORS_ALLOWED_ORIGINS`
6. ✅ Koristi HTTPS u produkciji
