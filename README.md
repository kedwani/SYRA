# SYRA Medical ID Platform

A hybrid medical identification platform designed for the Egyptian market, utilizing NFC and QR-enabled physical devices. SYRA empowers patients to store critical medical data securely and provides first responders with instant, life-saving access via a simple scan.

![Django](https://img.shields.io/badge/Django-5.x-green)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🌟 Features

### 👤 User Authentication & Identity
- **National ID Integration**: Registration requires a valid 14-digit Egyptian National ID
- **Smart Validation**: Automatic extraction and validation of birth date and century from the National ID
- **Role-based Access**: User, Doctor, Engineer, and Admin roles
- **Secure Access**: JWT-based authentication for all private API interactions
- **Doctor Verification**: License number validation for verified doctors

### 🏥 Medical Profile Management
- **Comprehensive Data**: Storage for blood type, allergies, chronic conditions, and immune diseases
- **Biometric Tracking**: Height and weight tracking for accurate emergency dosing
- **Privacy Controls**: Per-field visibility toggles (Public/Doctors-only)
- **Profile Sharing**: QR/NFC-enabled emergency profiles

### 💊 Medication & History Tracking
- **Medication Logs**: Track dosage, frequency, and duration (start/end dates)
- **Surgical History**: Logging of previous accidents, fractures, or major medical events with date tracking
- **Medical Events**: Complete timeline of medical history

### 👨‍👩‍👧‍👦 Emergency Contacts
- **Dual Contact Support**: Quick access to up to two emergency contacts per profile
- **Instant Dialing**: Optimized for mobile browser "click-to-call" functionality
- **Doctor-added Contacts**: Doctors can add emergency contacts on behalf of patients

### 🏪 E-Commerce Store
- **SYRA Bands**: QR/NFC-enabled medical identification bracelets
- **Multiple Designs**: Various colors, materials, and sizes
- **Band Registration**: Link physical bands to user profiles
- **Order Management**: Full order tracking with carriers

### 🔒 Privacy & Security
- **At-Rest Encryption**: Insurance card images are encrypted using Fernet symmetric encryption
- **Data Segregation**: Sensitive insurance data is only accessible via authenticated requests
- **UUID Masking**: Non-sequential UUIDs prevent ID enumeration (IDOR protection)
- **Rate Limiting**: Protection against API abuse
- **Access Logging**: Audit trail for all profile access

---

## 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.10+ | Backend language |
| Django 5.x | Web framework |
| Django REST Framework | API development & Serialization |
| SimpleJWT | Stateless authentication |
| Cryptography (Fernet) | Secure data encryption |
| SQLite / PostgreSQL | Database (Development / Production) |
| django-cors-headers | Cross-origin requests |
| drf-spectacular | API documentation |
| django-ratelimit | Rate limiting |

---

## 📂 Project Structure

```
SYRA/
├── syra/                          # Project Configuration
│   ├── __init__.py
│   ├── settings.py                # Django settings, JWT, CORS, Encryption config
│   ├── urls.py                    # Root URL routing
│   ├── wsgi.py                    # WSGI application
│   ├── asgi.py                    # ASGI application
│   └── middleware.py              # Custom middleware (language handling)
│
├── accounts/                      # User & Authentication App
│   ├── __init__.py
│   ├── models.py                  # SyraUser (Custom User Model)
│   ├── serializers.py             # Auth & Registration serializers
│   ├── views.py                   # API views & template views
│   ├── urls.py                    # URL patterns
│   ├── api_urls.py                # API URL patterns
│   ├── admin.py                   # Django admin configuration
│   ├── apps.py                    # App configuration
│   ├── tests.py                   # Unit tests
│   └── migrations/                # Database migrations
│
├── profiles/                      # Medical Data App (Core)
│   ├── __init__.py
│   ├── models.py                  # MedicalProfile, Medication, EmergencyContact, MedicalEvent
│   ├── serializers.py             # DRF serializers for API
│   ├── views.py                   # REST API views (ViewSets)
│   ├── template_views.py          # HTML template views
│   ├── urls.py                    # API URL patterns
│   ├── template_urls.py           # Template URL patterns
│   ├── signals.py                 # Django signals (auto-profile creation)
│   ├── medical_data.py            # Medication/diagnosis autocomplete data
│   ├── emergency_alerts.py        # Emergency alert & hospital lookup
│   ├── emergency_utils.py         # Emergency data encoding/decoding
│   ├── templatetags/
│   │   ├── emergency_tags.py      # Template tags for emergency views
│   │   └── qr_code.py             # QR code generation
│   ├── migrations/                # Database migrations
│   └── tests.py                   # Unit tests
│
├── store/                         # E-Commerce Store App
│   ├── __init__.py
│   ├── models.py                  # SyraBand, Order, BandRegistration, SavedAddress
│   ├── serializers.py             # Store serializers
│   ├── views.py                   # REST API views
│   ├── template_views.py           # Store template views
│   ├── urls.py                    # Store API URLs
│   ├── template_urls.py           # Store template URLs
│   ├── signals.py                 # Order & inventory signals
│   ├── emails.py                  # Transactional emails
│   ├── analytics.py               # Analytics utilities
│   ├── admin.py                   # Django admin
│   ├── context_processors.py      # Template context (cart)
│   ├── management/commands/       # Management commands
│   │   ├── seed_products.py      # Seed sample products
│   │   ├── check_inventory.py    # Check stock levels
│   │   └── add_sample_images.py   # Add sample band images
│   └── migrations/                # Database migrations
│
├── templates/                     # HTML Templates (Mobile-First)
│   ├── base.html                  # Base template with navbar/footer
│   ├── accounts/
│   │   ├── login.html            # Login page
│   │   └── register.html          # Registration page
│   ├── profiles/
│   │   ├── dashboard.html        # User dashboard
│   │   ├── profile_edit.html     # Profile editing with visibility toggles
│   │   ├── emergency_scan.html   # Emergency scan landing page (QR/NFC)
│   │   ├── medications.html      # Medication list
│   │   ├── contacts.html         # Emergency contacts
│   │   ├── events.html           # Medical events history
│   │   ├── doctor_portal.html    # Doctor portal
│   │   └── partials/             # Reusable template partials
│   └── store/
│       ├── home.html             # Store homepage
│       ├── band_list.html        # Band catalog
│       ├── band_detail.html      # Band details
│       ├── cart.html             # Shopping cart
│       ├── checkout.html         # Checkout page
│       ├── order_list.html       # User orders
│       └── order_detail.html     # Order details
│
├── media/                        # User-uploaded files
│   ├── logo.png                   # Site logo
│   ├── insurance/                 # Insurance card images (encrypted)
│   └── store/                     # Product images
│
├── locale/                        # Internationalization
│   └── ar/                        # Arabic translations
│
├── docs/                         # Documentation
│   └── patient-medical-profile-visibility-system.md
│
├── .kilocode/                    # Kilocode configuration
├── .github/                      # GitHub workflows
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
├── AGENTS.md                     # Agent rules
├── frontend-design-guide.md       # Frontend design guidelines
└── README.md                     # This file
```

---

## 🔗 Component Relationships

```
User Request
    │
    ▼
┌─────────────────────────────────────────────┐
│              syra/urls.py                    │
│  (Routes to accounts/, profiles/, store/)  │
└─────────────────────────────────────────────┘
    │
    ├──────────────────┬──────────────────────┐
    ▼                  ▼                      ▼
┌────────────┐   ┌────────────┐         ┌────────────┐
│ accounts/  │   │ profiles/  │         │   store/   │
│   App      │   │   App      │         │    App     │
└────────────┘   └────────────┘         └────────────┘
    │                  │                      │
    ▼                  ▼                      ▼
┌────────────┐   ┌────────────┐         ┌────────────┐
│ SyraUser   │   │ Medical    │         │   Order    │
│ Model      │   │ Profile    │         │   Model    │
└────────────┘   └────────────┘         └────────────┘
    │                  │                      │
    │                  │                      ▼
    │                  │              ┌────────────┐
    │                  │              │  SyraBand  │
    │                  │              │  Model     │
    │                  │              └────────────┘
    │                  │                      │
    └──────────────────┴──────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │   Templates/   │
              │  (HTML Views)  │
              └────────────────┘
```

---

## 🚀 Installation

### 1. Prerequisites
- Python 3.10 or higher
- Virtualenv package installed

### 2. Setup Environment

```bash
# Clone and enter project
git clone <repository-url>
cd syra

# Create and activate virtual environment
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root directory:

```env
# Required
DJANGO_SECRET_KEY=your-django-secret-key
FERNET_KEY=your-fernet-key-generated-via-cryptography

# Optional (with defaults)
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

Generate keys with:
```bash
# Django Secret Key
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Fernet Key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 4. Initialize Database

```bash
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```

---

## 📋 API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/accounts/register/` | User registration |
| POST | `/api/accounts/login/` | JWT token login |
| POST | `/api/accounts/token/refresh/` | Refresh JWT token |

### Emergency Access (Public)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profiles/emergency/<uuid>/` | HTML View: Optimized for QR/NFC scanning |
| GET | `/api/profiles/scan/<uuid>/` | JSON View: Core medical data for apps |
| GET | `/api/profiles/access/<uuid>/` | Check access permissions |
| POST | `/api/profiles/reveal-all-data/<uuid>/` | Reveal full data (doctor/owner) |

### Medical Management (Private - JWT Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/PUT | `/api/profiles/profiles/<uuid>/` | Manage personal medical data |
| GET/POST | `/api/profiles/medications/` | CRUD for medications |
| GET/POST | `/api/profiles/contacts/` | Manage emergency contacts (Max 2) |
| GET/POST | `/api/profiles/events/` | Medical events history |
| GET | `/api/profiles/search/` | Search medications/diagnoses |

### Store (Private - JWT Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/store/band-types/` | List available band types |
| GET/POST | `/api/store/orders/` | Manage orders |
| GET | `/api/store/bands/<id>/` | Band details |

---

## 🔐 Security Highlights

1. **National ID Validation**: Validated against Egyptian Civil Status format (Century-YYMMDD-SS-KKK-C)
2. **Image Encryption**: Insurance photos stored as encrypted blobs using Fernet
3. **Privacy by Default**: Emergency scan excludes National ID and Insurance Photo
4. **Rate Limiting**: 30 requests/minute for emergency endpoints
5. **Access Logging**: All profile access is logged for audit purposes

---

## 🌍 Internationalization

- **English (en)**: Default language
- **Arabic (ar)**: Full translation support

Language can be switched via:
- URL parameter: `?lang=ar`
- Cookie: `django_language`
- Session: `_language`

---

## 📱 Mobile-First Design

The templates are built with a mobile-first approach:
- Responsive layouts using CSS Grid and Flexbox
- Touch-friendly buttons and inputs
- Fast-loading HTMX partials for emergency data
- Click-to-call for emergency contacts

---

## 👨‍💻 Author

Mahmoud – Backend Developer

---

## 📄 License

MIT License
