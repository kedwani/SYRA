# SYRA - Emergency Medical Bracelet System

A Django-based emergency medical bracelet system that provides quick access to critical medical information through QR codes. Designed for healthcare accessibility in emergency situations.

## Features

### Core Functionality
- **QR Code Generation** - Automatic QR code generation linked to user medical profiles
- **Emergency Access** - Fast, cached public endpoints for first responders
- **Medical Data Management** - Track allergies, medications, conditions, and emergency contacts
- **Bracelet Management** - Hardware integration with claim PIN system

### User Management
- JWT-based authentication with access/refresh tokens
- Custom user model with medical-specific fields (blood type, date of birth)
- Medical personnel verification system
- Premium subscription support

### API Endpoints
- RESTful API design following Django REST Framework best practices
- Rate limiting on public emergency endpoints
- Redis caching for sub-100ms emergency response times

## Tech Stack

### Backend
- **Framework**: Django 5.2+
- **API**: Django REST Framework
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Cache**: Redis
- **Authentication**: JWT (pyjwt)

### Frontend (Coming Soon)
- Next.js 15 with React
- TypeScript
- Tailwind CSS

## Project Structure

```
syra/
├── syra/                    # Django project settings
│   └── settings/           # Split settings (base/dev/prod)
├── apps/                   # Django applications
│   ├── accounts/           # User management & auth
│   ├── profiles/           # Medical profiles & QR codes
│   ├── medical/            # Medical data models
│   ├── emergency/          # Public emergency endpoints
│   ├── hardware/           # Bracelet management
│   ├── store/              # E-commerce
│   └── common/             # Shared utilities
├── requirements/           # Python dependencies
├── docs/                  # Architecture documentation
└── manage.py
```

## Getting Started

### Prerequisites
- Python 3.10+
- Redis (for caching)
- PostgreSQL (for production)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/syra.git
   cd syra
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements/base.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server:**
   ```bash
   python manage.py runserver
   ```

### Running Tests
```bash
python manage.py test
```

## API Documentation

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register/` | POST | Register new user |
| `/api/v1/auth/login/` | POST | User login |
| `/api/v1/auth/refresh/` | POST | Refresh JWT token |
| `/api/v1/auth/logout/` | POST | Logout |

### Profiles
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/profiles/me/` | GET/PUT | Current user's profile |
| `/api/v1/profiles/qr/` | GET | Get QR code |
| `/api/v1/profiles/qr/rotate/` | POST | Rotate QR code |

### Medical Data
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/medical/allergies/` | GET/POST | Manage allergies |
| `/api/v1/medical/medications/` | GET/POST | Manage medications |
| `/api/v1/medical/conditions/` | GET/POST | Manage conditions |
| `/api/v1/medical/emergency-contacts/` | GET/POST | Manage contacts |

### Emergency (Public)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/e/{qr_hash}/` | GET | Basic emergency info |
| `/api/v1/e/{qr_hash}/critical/` | GET | Critical data (cached) |
| `/api/v1/e/{qr_hash}/extended/` | GET | Full medical data |

### Hardware
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/bracelets/my-bracelets/` | GET | User's bracelets |
| `/api/v1/bracelets/claim/` | POST | Claim a bracelet |

### E-commerce
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/products/` | GET | List products |
| `/api/v1/orders/` | GET/POST | Manage orders |

## Security

- JWT authentication with short-lived access tokens (15 min)
- Rate limiting on emergency endpoints (20 req/min)
- Field-level encryption for sensitive data
- CORS configuration
- Password validation
- Audit logging

## Deployment

### Docker
```bash
docker-compose up -d
```

### Production Settings
Set `DJANGO_SETTINGS_MODULE=syra.settings.production` and configure:
- PostgreSQL database
- Redis cache
- S3 for media storage
- HTTPS/TLS

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and feature requests, please open an issue on GitHub.