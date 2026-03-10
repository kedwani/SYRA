# SYRA — Smart Medical ID System 🏥🇪🇬

**SYRA** is a secure medical backend platform built for the Egyptian market. It powers smart medical wristbands and keychains equipped with **QR codes** and **NFC** technology, giving first responders and doctors instant access to life-saving patient data in emergencies.

---

## 🚨 The Problem

In Egypt, critical patient data is often on paper — lost, illegible, or simply unavailable in emergencies. **SYRA** solves this by digitising medical records and making them accessible in seconds via a wristband scan.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔐 **Custom Auth** | `AbstractUser`-based model with Egyptian National ID field |
| 📋 **Full Medical Profile** | Blood type, chronic diseases, medical history, allergies, notes |
| 💊 **Medications** | Tracked with start date and duration |
| 🆘 **Emergency Contacts** | Up to 2 prioritised contacts per patient |
| 🔒 **Encrypted Insurance** | Card image encrypted at rest using Fernet symmetric encryption |
| 🚫 **Privacy-First API** | Insurance data lives on a **separate endpoint** — never exposed in the general profile view |
| ⚡ **Django Signals** | `MedicalProfile` auto-created on user registration |
| 🔎 **Patient Search** | Find patients by username or QR/NFC UUID |
| 🎫 **JWT Auth** | Stateless, token-based authentication |

---

## 🛠️ Tech Stack

- **Framework:** Django 5.x + Django REST Framework 3.x
- **Auth:** `djangorestframework-simplejwt`
- **Encryption:** `cryptography` (Fernet symmetric encryption)
- **Database:** SQLite (development) — swap to PostgreSQL for production
- **Language:** Python 3.12+

---

## 📁 Project Structure

```
SYRA/
├── Accounts/           # Custom User Model + Auth endpoints
│   ├── models.py       # SyraUser (AbstractUser + national_id)
│   ├── serializers.py  # Registration + user detail
│   ├── views.py        # Register, JWT login, /me
│   ├── urls.py
│   ├── admin.py
│   └── apps.py         # Imports Profiles.signals on ready()
│
├── Profiles/           # Medical data
│   ├── models.py       # MedicalProfile, EmergencyContact, Medication, MedicalEvent
│   ├── signals.py      # Auto-create MedicalProfile on user save
│   ├── serializers.py  # Profile + Insurance serializers
│   ├── views.py        # All profile views + PatientSearchView
│   ├── urls.py
│   └── admin.py
│
├── Syra/               # Project config
│   ├── settings.py
│   └── urls.py
│
├── requirements.txt
├── manage.py
└── README.md
```

---

## ⚙️ Setup

### 1. Clone & install

```bash
git clone https://github.com/kedwani/SYRA.git
cd SYRA
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file (or export variables):

```bash
# Generate a Fernet key ONCE and store it securely
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

```env
SECRET_KEY=your-django-secret-key
SYRA_ENCRYPTION_KEY=your-fernet-key-from-above
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

> ⚠️ **Never commit** `.env` to version control. The `.gitignore` already excludes it.

### 3. Migrate & run

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 🔗 API Endpoints

### Authentication — `/api/auth/`

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/auth/register/` | Register new user (auto-creates profile) | ❌ Open |
| POST | `/api/auth/token/` | Obtain JWT access + refresh tokens | ❌ Open |
| POST | `/api/auth/token/refresh/` | Refresh access token | ❌ Open |
| GET | `/api/auth/me/` | Get current user info | ✅ JWT |

### Profiles — `/api/profile/`

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/profile/search/?q=<query>` | Search by username or QR UUID | ✅ JWT |
| GET | `/api/profile/<username>/` | Get medical profile (no insurance) | ✅ JWT |
| PUT | `/api/profile/<username>/` | Update profile (owner only) | ✅ JWT (owner) |
| GET | `/api/profile/<username>/insurance/` | Get decrypted insurance card | ✅ JWT (owner) |
| PUT | `/api/profile/<username>/insurance/` | Upload / update insurance card | ✅ JWT (owner) |
| GET | `/api/profile/<username>/contacts/` | List emergency contacts | ✅ JWT |
| POST | `/api/profile/<username>/contacts/` | Add emergency contact (max 2) | ✅ JWT |
| PUT | `/api/profile/<username>/contacts/<id>/` | Update contact | ✅ JWT |
| DELETE | `/api/profile/<username>/contacts/<id>/` | Delete contact | ✅ JWT |
| GET | `/api/profile/<username>/medications/` | List medications | ✅ JWT |
| POST | `/api/profile/<username>/medications/` | Add medication | ✅ JWT |
| PUT | `/api/profile/<username>/medications/<id>/` | Update medication | ✅ JWT |
| DELETE | `/api/profile/<username>/medications/<id>/` | Delete medication | ✅ JWT |
| GET | `/api/profile/<username>/history/` | Get medical event history | ✅ JWT |
| POST | `/api/profile/<username>/history/` | Add medical event | ✅ JWT |

---

## 🔐 Security Design

### Insurance Image Encryption

Insurance card photos are **never stored as plain files**. Before saving, `Profiles/models.py` encrypts the raw bytes using **Fernet symmetric encryption** (from the `cryptography` library):

```python
# Encryption on upload
encrypted_bytes = Fernet(key).encrypt(raw_bytes)
storage.save("insurance/.../file.enc", ContentFile(encrypted_bytes))

# Decryption on read (only via /insurance/ endpoint)
raw_bytes = Fernet(key).decrypt(cipher_bytes)
```

The decrypted image is returned as a **base64 JSON field** — it never hits the filesystem unencrypted.

### Privacy Separation

The `/api/profile/<username>/` endpoint **deliberately excludes** all insurance fields. Insurance data is only available via `/api/profile/<username>/insurance/` and is restricted to the **profile owner** by `IsProfileOwner` permission class.

---

## 👨‍💻 Author

**Mahmoud Nasser (Kedwani)** — Backend Developer