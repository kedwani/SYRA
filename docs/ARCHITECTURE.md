# SYRA Technical Architecture Recommendation

## Optimal Framework Selection

### Frontend: Next.js 15 (React)
- **Rationale**: Fast initial load for emergency access interface, SSR + Edge caching, excellent for patient-facing apps, strong TypeScript support, large talent pool
- **Alternative**: Flutter/React Native for mobile apps (cross-platform)

### Backend: Django (Python) + FastAPI
- **Rationale**: Your existing codebase uses Django 5.2. Django provides built-in security (SQL injection, XSS protection), admin panel, and ORM—ideal for healthcare. Add FastAPI for high-performance async endpoints where needed
- **Microservices option**: NestJS (Node.js) for real-time features (emergency alerts, WebSocket)

### Database
- **Primary**: PostgreSQL (ACID compliance, row-level security for PHI)
- **Cache**: Redis (session, API caching)
- **Search**: Elasticsearch (patient profile search)

### Infrastructure: AWS or Google Cloud (HIPAA-eligible)

---

## Architecture Overview

```
CDN (CloudFlare/AWS CloudFront)
|
|  +---------------------+    +--------------------------------+
|  |  Next.js Frontend   |    |   Emergency Access Interface   |
|  |  (SaaS + E-commerce) |    |   (Static, Fast-loading)        |
|  +---------+-----------+    +---------------+----------------+
|            |                                   |
|            v                                   v
|  +-------------------------------------------------------+
|  |                    API Gateway (Kong/AWS API Gateway) |
|  |              Rate Limiting • Auth • Logging          |
|  +---------------------------+---------------------------+
|                              |
|      +----------------------++----------------------+
|      v                      v                      v
| +-----------+      +-------------+        +---------------+
| | SaaS API  |      | Emergency   |        | E-commerce    |
| | (Django)  |      | API (Fast)  |        | API (Stripe)  |
| +-----+-----+      +------+------+        +-------+-------+
|       |                    |                      |
|       v                    v                      v
| +-----------+      +-------------+        +---------------+
| | PostgreSQL|      | Read Replica|        | Stripe/PayPal |
| | (PHI Data)|      | (Cache)    |        | Payment GW    |
| +-----------+      +-------------+        +---------------+
```

---

## API Design

### REST Endpoints (Django REST Framework)

```
/api/v1/
├── /auth/
│   ├── POST /register/          # User registration
│   ├── POST /login/             # JWT token issuance
│   ├── POST /refresh/           # Token refresh
│   └── POST /logout/            # Invalidate tokens
│
├── /profiles/
│   ├── GET /me/                 # Current user's profile
│   ├── PUT /me/                 # Update profile
│   ├── GET /{qr_id}/            # Publicemergency data (no auth)
│   └── GET /{qr_id}/extended/   # Medical personnel access
│
├── /medical/
│   ├── GET/POST/PUT/DELETE /allergies/
│   ├── GET/POST/PUT/DELETE /medications/
│   ├── GET/POST/PUT/DELETE /conditions/
│   └── GET/POST/PUT/DELETE /emergency-contacts/
│
├── /bracelets/
│   ├── GET /my-bracelets/       # User's linked bracelets
│   ├── POST /link/              # Link QR to profile
│   └── GET /{serial}/status/    # Check linkage status
│
├── /products/                   # E-commerce
│   ├── GET /                    # List bracelets
│   ├── GET /{id}/               # Product details
│   └── POST /order/             # Create order
│
└── /subscriptions/
    ├── GET /status/             # Premium status
    └── POST /subscribe/         # Subscribe to premium
```

### Authentication Strategy

| User Type | Method | Token Type |
|-----------|--------|-------------|
| Regular users | Email/Password + MFA | JWT (short-lived, 15min) |
| Medical personnel | OAuth 2.0 (hospital verification) | JWT with scope: "medical" |
| Emergency access | QR scan | Stateless (no token) |

### Security Implementation

```
Security Layers:
---------------------------------------------------------------
1. TLS 1.3 (all connections)
2. AES-256 encryption at rest (PHI)
3. Field-level encryption for sensitive data
4. JWT + refresh tokens with httpOnly cookies
5. Rate limiting (100 req/min regular, 20 req/min emergency)
6. Audit logging (who accessed what, when)
7. HIPAA BAA with cloud provider
```

---

## Real-Time Features (Optional)

- **WebSocket**: NestJS microservice for emergency notifications
- **Use cases**: 
  - Hospital verifies medical personnel credentials
  - User receives alert when bracelet is scanned
  - Live chat with medical personnel

---

## Scalability Strategy

### Horizontal Scaling
- **Stateless API servers** behind load balancer
- **PostgreSQL read replicas** for emergency access queries
- **Redis cluster** for session/cache

### Caching Strategy

```
Emergency Data Cache (CDN/Redis)
- TTL: 5 minutes
- Cache key: qr_{id}_critical

Profile Data (Redis)
- TTL: 1 hour
- User-specific cache

Static Assets (CDN)
- Images, CSS, JS
```

---

## Deployment Strategy

### Infrastructure
- **Cloud**: AWS (eu-west-1 primary, eu-west-2 failover)
- **Container**: Docker + Kubernetes (EKS)
- **CI/CD**: GitHub Actions

### Environment Setup

```
Production Pipeline
1. Code push to main
2. GitHub Actions: lint, test, scan
3. Build Docker image
4. Deploy to EKS (canary)
5. Health checks pass
6. Route traffic to new version
```

### Monitoring
- **Metrics**: Prometheus + Grafana
- **Logs**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Alerts**: PagerDuty for critical issues

---

## Summary

| Layer | Technology | Justification |
|-------|------------|---------------|
| Frontend | Next.js 15 | Fast emergency access, SSR, edge caching |
| Backend | Django 5.2 + FastAPI | Existing codebase, built-in security, admin panel |
| Database | PostgreSQL | ACID, HIPAA compliance |
| Cache | Redis | Performance for read-heavy emergency access |
| Auth | JWT + OAuth 2.0 | Flexible authentication for different user types |
| Cloud | AWS/GCP | HIPAA-eligible, global CDN |

This architecture prioritizes **speed for emergency access** (cached static page), **security for PHI data** (encryption, audit logs), and **scalability for growth** (microservices-ready, horizontal scaling).

---

## Next Steps

1. Migrate from SQLite to PostgreSQL
2. Set up Django REST Framework
3. Configure PostgreSQL with encryption
4. Set up Redis for caching
5. Implement JWT authentication
6. Create emergency access API endpoint (public, cached)
7. Set up monitoring infrastructure

---

# DETAILED ARCHITECTURE REVIEW & RECOMMENDATIONS

## Current Project State

The SYRA project is a fresh Django 5.2 installation with:
- Default SQLite database (needs migration to PostgreSQL)
- No custom apps created yet
- Empty URL configuration
- DEBUG=True in settings

This is the **perfect time** to implement the recommended architecture.

---

## ✅ STRENGTHS OF THE PROPOSED ARCHITECTURE

### 1. Emergency-First Design ✅
The priority-based data loading for emergency access is excellent:
- **Allergies** → **Blood type** → **Critical conditions** → extended data
- Redis caching with 5-minute TTL ensures sub-100ms response times

**Recommendation**: Add a dedicated `/emergency/` endpoint that bypasses authentication entirely but uses rate limiting + CAPTCHA for abuse prevention.

### 2. QR Security Strategy ✅
Using UUID + hash instead of sequential IDs prevents:
- Data scraping attacks
- Profile enumeration
- Brute-force guessing

**Recommendation**: Add an "QR rotation" feature that allows users to regenerate their QR code if compromised, invalidating the old one.

### 3. Data Visibility System ✅
Three-tier visibility (public/doctor/private) is exactly right for healthcare:

```python
class VisibilityLevel:
    PUBLIC = "public"        # Anyone who scans
    DOCTOR = "doctor"        # Verified medical personnel
    PRIVATE = "private"      # Only the user
```

**Recommendation**: Add a "scan history" feature so users can see who accessed their data (for privacy transparency).

### 4. E-commerce Integration ✅
The flow (Product → QR → Profile) is correct, but add:
- **One-time-use QR codes** for demo/trial purposes
- **QR linking status tracking** (linked, pending, expired)

---

## 🔧 RECOMMENDATIONS & IMPROVEMENTS

### 1. Backend Folder Structure

```
syra/                          # Project root
├── config/                    # Django settings (split for production)
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py           # Shared settings
│   │   ├── local.py          # Development
│   │   └── production.py     # Production (secure defaults)
│   ├── urls.py
│   └── asgi.py
├── apps/                      # Django applications
│   ├── core/                 # Shared functionality
│   │   ├── models.py
│   │   ├── permissions.py
│   │   └── validators.py
│   ├── accounts/             # User management
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── profiles/             # Medical profiles
│   │   ├── models.py
│   │   ├── views.py
│   │   └── signals.py        # Cache invalidation on profile update
│   ├── emergency/            # Emergency access (public)
│   │   ├── views.py          # High-performance cached endpoints
│   │   └── middleware.py     # Rate limiting
│   ├── qr/                   # QR code management
│   │   ├── models.py
│   │   ├── services.py       # QR generation/validation
│   │   └── management/
│   ├── medical/              # Medical data (allergies, meds, etc.)
│   │   ├── models.py
│   │   └── managers.py
│   ├── products/             # E-commerce products
│   │   ├── models.py
│   │   └── views.py
│   ├── orders/               # Order management
│   │   └── models.py
│   └── subscriptions/        # Premium subscriptions
├── common/                   # Shared utilities
│   ├── cache.py              # Redis helpers
│   ├── encryption.py         # Field-level encryption
│   └── audit.py              # Audit logging
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── manage.py
```

### 2. Frontend Folder Structure (Next.js)

```
frontend/
├── app/
│   ├── (auth)/               # Auth routes (login, register)
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/          # Protected routes
│   │   ├── dashboard/
│   │   ├── profile/
│   │   ├── medical/
│   │   ├── bracelets/
│   │   ├── shop/
│   │   └── settings/
│   ├── e/                    # Emergency access (public, no layout)
│   │   └── [qr_id]/
│   ├── api/                  # API routes (if needed)
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ui/                   # Reusable UI components
│   ├── forms/                # Form components
│   ├── medical/              # Medical data components
│   └── emergency/            # Emergency interface components
├── lib/
│   ├── api.ts                # API client
│   ├── auth.ts               # Auth utilities
│   └── utils.ts
├── hooks/                    # Custom React hooks
├── types/                    # TypeScript types
├── public/
│   └── assets/
└── .env.local
```

### 3. Database Schema Recommendations

```python
# Core models recommended structure

class User(AbstractUser):
    """Extended user with healthcare-specific fields"""
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    blood_type = models.CharField(max_length=5, choices=BLOOD_TYPES)
    avatar = models.ImageField(upload_to='avatars/')
    is_medical_personnel = models.BooleanField(default=False)
    medical_license_number = models.CharField(max_length=50, blank=True)
    hospital_verified = models.BooleanField(default=False)

class MedicalProfile(models.Model):
    """Main profile linked to QR code"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    qr_token = models.UUIDField(unique=True, db_index=True)
    qr_token_hash = models.CharField(max_length=128)  # For URL-friendly codes
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Allergy(models.Model):
    profile = models.ForeignKey(MedicalProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_LEVELS)

class Medication(models.Model):
    profile = models.ForeignKey(MedicalProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_LEVELS)

class EmergencyContact(models.Model):
    profile = models.ForeignKey(MedicalProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

class Bracelet(models.Model):
    """Physical bracelet linked to user"""
    serial_number = models.CharField(max_length=50, unique=True)
    qr_code = models.ImageField(upload_to='qrcodes/')
    profile = models.ForeignKey(MedicalProfile, null=True, blank=True)
    status = models.CharField(choices=BRACELET_STATUS)
    ordered_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
```

### 4. API Endpoint Refinements

```python
# Emergency endpoints - optimized for speed
urlpatterns = [
    # Public emergency access - NO auth required
    path('e/<uuid:qr_token>/', EmergencyPublicView.as_view(), name='emergency-public'),
    path('e/<uuid:qr_token>/critical/', EmergencyCriticalView.as_view(), name='emergency-critical'),
    
    # Medical personnel access - requires verification
    path('e/<uuid:qr_token>/extended/', EmergencyExtendedView.as_view(), name='emergency-extended'),
    
    # QR code management
    path('qr/generate/', QRGenerateView.as_view(), name='qr-generate'),
    path('qr/rotate/', QRRotateView.as_view(), name='qr-rotate'),
    path('qr/validate/<str:qr_string>/', QRValidateView.as_view(), name='qr-validate'),
]
```

### 5. Critical Security Recommendations

| Area | Recommendation | Priority |
|------|----------------|----------|
| QR Token | Use URL-safe Base64 encoded UUID + HMAC signature | 🔴 High |
| Rate Limiting | 100 req/min normal, 20 req/min emergency endpoint | 🔴 High |
| Field Encryption | Use `django-fernet-fields` or `cryptography` for PHI | 🔴 High |
| Audit Logging | Log ALL emergency access attempts (successful + failed) | 🔴 High |
| Session Management | Short JWT (15 min) + refresh tokens, httpOnly cookies | 🟡 Medium |
| Input Validation | Use Pydantic-style validation, reject unexpected fields | 🟡 Medium |
| CORS | Strict origin whitelist, no wildcard | 🟡 Medium |

### 6. Caching Strategy Details

```python
# Redis cache keys structure
CACHE_KEYS = {
    'emergency_critical': 'qr:{qr_token}:critical',     # 5 min TTL
    'emergency_extended': 'qr:{qr_token}:extended',     # 5 min TTL
    'user_profile': 'user:{user_id}:profile',           # 1 hour TTL
    'user_medical': 'user:{user_id}:medical',           # 1 hour TTL
}

# Cache invalidation signals
@receiver(post_save, sender=Allergy)
def invalidate_allergy_cache(sender, instance, **kwargs):
    profile = instance.profile
    redis.delete(f'qr:{profile.qr_token}:critical')
    redis.delete(f'qr:{profile.qr_token}:extended')
```

### 7. Performance Optimizations

1. **Database Indexes**:
   - `qr_token` on MedicalProfile (unique index)
   - `serial_number` on Bracelet (unique index)
   - Composite index on (profile, visibility) for medical data queries

2. **Query Optimization**:
   - Use `select_related()` and `prefetch_related()` for profile queries
   - Denormalize critical emergency data into a single cached JSON blob

3. **CDN Strategy**:
   - Static emergency page served from edge (Cloudflare Workers)
   - API responses cached at CDN level with appropriate Cache-Control headers

---

## 📋 IMPLEMENTATION PRIORITY

| Phase | Tasks | Timeline |
|-------|-------|----------|
| **Phase 1** | Django project setup, PostgreSQL, Redis, User + Profile models | Week 1-2 |
| **Phase 2** | Medical data models (Allergies, Medications, Conditions), CRUD APIs | Week 2-3 |
| **Phase 3** | QR generation + emergency public endpoint with caching | Week 3-4 |
| **Phase 4** | Frontend (Next.js) - Dashboard, Profile management | Week 4-6 |
| **Phase 5** | E-commerce (Products, Orders, Stripe integration) | Week 6-8 |
| **Phase 6** | Medical personnel verification, extended access | Week 8-9 |
| **Phase 7** | Security hardening, audit logging, HIPAA compliance | Week 9-10 |

---

## ✅ FINAL VERDICT

The proposed architecture is **solid and well-suited** for SYRA. Key takeaways:

1. **Stick with Django + Next.js** - Your existing code aligns with this
2. **Prioritize emergency endpoint performance** - This is your USP
3. **Implement field-level encryption** - Critical for HIPAA
4. **Add audit logging from day one** - Easier to add now than retroactively
5. **Use the suggested folder structure** - Scalable and maintainable

The architecture is production-ready and will scale with your business.

---

# ADDITIONAL IMPROVEMENTS & REFINEMENTS

## 1. Simplified Architecture (No Premature Microservices)

**Original concern**: Generic API Gateway adds complexity for MVP

**Solution**: Use Django's built-in URL routing + Nginx for simplicity

```
┌─────────────────────────────────────────────────────────────────┐
│                    Simplified MVP Architecture                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [ Next.js BFFs ]                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Dashboard   │  │  Emergency   │  │     Shop     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           ▼                                     │
│              [ Django REST API (Monolithic) ]                  │
│              - Rate Limiting (django-ratelimit)                 │
│              - Authentication (JWT)                             │
│              - CORS + Security Headers                          │
│                           │                                     │
│     ┌─────────────────────┼─────────────────────┐              │
│     ▼                     ▼                     ▼              │
│  ┌──────┐           ┌──────────┐         ┌──────────┐         │
│  │ Auth │           │ Medical  │         │  E-com   │         │
│  │      │           │  Data    │         │ Products │         │
│  └──┬───┘           └────┬─────┘         └────┬─────┘         │
│     │                    │                     │                │
│     └────────────────────┼─────────────────────┘                │
│                          ▼                                       │
│              [ PostgreSQL + pgcrypto ]                         │
│              (Field-level encryption at rest)                   │
│                          │                                       │
│                          ▼                                       │
│              [ Redis (Snapshots) ]                              │
│                          │                                       │
│                          ▼                                       │
│              [ S3: Bracelet Images/QRs ]                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**When to add API Gateway**: Only when scaling to 10k+ users or needing complex routing

---

## 2. Rate Limiting & Encryption Details

### Rate Limiting (django-ratelimit)

```python
# settings.py
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_DEFAULT = '100/m'  # Regular users
RATELIMIT_EMERGENCY = '20/m'  # Emergency endpoints (stricter)

# views.py
from django_ratelimit.decorators import ratelimit

class EmergencyPublicView(APIView):
    authentication_classes = []  # No auth needed
    permission_classes = [AllowAny]
    
    @ratelimit(key='ip', rate='20/m', method='GET', block=True)
    def get(self, request, qr_token):
        # Emergency access logic
        pass
```

### Field-Level Encryption (pgcrypto)

```sql
-- Enable pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypted column example
ALTER TABLE medical_profile 
ADD COLUMN sensitive_data_encrypted BYTEA;

-- Encryption function
CREATE OR REPLACE FUNCTION encrypt_medical_data(data TEXT, key BYTEA)
RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(data, key);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Decryption function
CREATE OR REPLACE FUNCTION decrypt_medical_data(data BYTEA, key BYTEA)
RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(data, key);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

## 3. Doctor Verification Flow

**Improvement**: Use Twilio Verify or Google reCAPTCHA Enterprise instead of custom flows

```
┌─────────────────────────────────────────────────────────────────┐
│                 Doctor Verification Flow                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Doctor registers with:                                      │
│     - Email (hospital domain)                                   │
│     - License number                                            │
│     - Hospital name                                              │
│                                                                  │
│  2. Verification options:                                       │
│                                                                  │
│     Option A: Twilio Verify (SMS)                               │
│     ┌─────────────────────────────────────────┐                 │
│     │  User enters phone → OTP → Verified    │                 │
│     └─────────────────────────────────────────┘                 │
│                                                                  │
│     Option B: Google reCAPTCHA Enterprise                        │
│     ┌─────────────────────────────────────────┐                 │
│     │  Hospital admin validates → Badge shown │                 │
│     └─────────────────────────────────────────┘                 │
│                                                                  │
│  3. Result: is_verified_medical_personnel = True               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

```python
# Doctor verification service
class DoctorVerificationService:
    @staticmethod
    def verify_with_twilio(phone, otp_code):
        from twilio.rest import Client
        client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
        verification = client.verification \
            .services(settings.TWILIO_SERVICE_SID) \
            .verifications.check(phone, otp_code)
        return verification.status == 'approved'
    
    @staticmethod
    def verify_with_hospital_api(license_number, hospital_id):
        # Integrate with hospital verification API
        # Eg: Egyptian Medical Syndicate API
        pass
```

---

## 4. BFF Pattern Implementation

**Pattern**: Next.js acts as Backend-For-Frontend, tailoring responses

```typescript
// frontend/lib/api/emergency.ts
// Minimal JSON for emergency - only critical data

export async function getEmergencyData(qrId: string) {
  const response = await fetch(`/api/emergency/${qrId}/critical`);
  return response.json(); // Returns: { allergies, bloodType, conditions }
}

// frontend/app/e/[qr_id]/page.tsx
// Server Component - SSR with Redis cache
export default async function EmergencyPage({ params }: { params: { qr_id: string } }) {
  const data = await getEmergencyData(params.qr_id);
  
  return (
    <div className="emergency-view">
      <CriticalAlert data={data} />
      {/* Above fold - critical only */}
    </div>
  );
}
```

---

## 5. Deployment Strategy (MVP → Production)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Deployment Stages                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  STAGE 1: Development (Weeks 1-4)                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Railway / Render                                           ││
│  │  - Django + PostgreSQL + Redis                               ││
│  │  - Next.js static export                                     ││
│  │  - Cost: ~$25/month                                          ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  STAGE 2: Production Launch (Month 2-3)                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  AWS ECS / DigitalOcean App Platform                         ││
│  │  - Docker containers                                         ││
│  │  - Managed PostgreSQL (RDS)                                  ││
│  │  - ElastiCache Redis                                          ││
│  │  - S3 for media                                              ││
│  │  - CloudFront CDN                                            ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  STAGE 3: Scale (10k+ users)                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  AWS EKS (Kubernetes)                                        ││
│  │  - Auto-scaling                                              ││
│  │  - RDS Read Replicas                                         ││
│  │  - Redis Cluster                                             ││
│  │  - API Gateway + WAF                                         ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Enhanced Folder Structure (Streamlined)

```
/backend
  /core                    # Settings, URLs, WSGI
    settings/
      __init__.py
      base.py
      development.py
      production.py
  /apps
    /users                # User profiles, auth
      models.py
      views.py
      urls.py
    /medical             # Allergies, conditions, visibility
      models.py
      views.py
      managers.py
    /emergency           # QR scans, public endpoints
      views.py
      middleware.py
    /ecommerce            # Products, orders, stripe
      models.py
      views.py
      webhooks.py
    /qrgen               # UUID generation, hashes
      services.py
  /api
    serializers.py
    views.py

/frontend
/app
  /(auth)/
    login/page.tsx
    register/page.tsx
  /dashboard/
    profile/page.tsx
    medical/page.tsx
  /e/
    [qr_id]/page.tsx     # Emergency SSR + Redis fetch
  /shop/
    products/page.tsx
    checkout/page.tsx
  /api/
    route.ts             # Optional proxy
/components
  /ui
  /medical
/lib
  api.ts
  auth.ts
  utils.ts
```

---

## 7. Security Recommendations

| Area | Implementation | Priority |
|------|----------------|----------|
| HTTPS | Mandate TLS 1.3, redirect HTTP→HTTPS | 🔴 Critical |
| OWASP Django-DEF | Use django-defense for security headers | 🔴 Critical |
| Audit Logs | Log ALL medical access (who, when, what) | 🔴 Critical |
| Rate Limiting | Django Ratelimit on /qr/{id} endpoints | 🔴 Critical |
| S3 Presigned URLs | Temporary URLs for medical documents | 🔴 Critical |
| SOC 2 | Pursue early if dealing with enterprise clients | 🟡 High |
| WAF | AWS WAF after 1k users | 🟡 Medium |

### S3 Presigned URLs for Medical Documents

```python
# services/s3_service.py
import boto3
from django.conf import settings

class S3Service:
    def __init__(self):
        self.client = boto3.client('s3')
        self.bucket = settings.AWS_STORAGE_BUCKET_NAME
    
    def generate_presigned_url(self, key: str, expires_in: int = 600):
        """
        Generate temporary URL for medical documents.
        Default expires in 10 minutes for emergency access.
        """
        return self.client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket,
                'Key': key
            },
            ExpiresIn=expires_in  # 10 minutes
        )
    
    def upload_presigned_url(self, key: str, content_type: str):
        """Generate URL for secure upload"""
        return self.client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': self.bucket,
                'Key': key,
                'ContentType': content_type
            },
            ExpiresIn=3600  # 1 hour for upload
        )
```

### Django Ratelimit for QR Endpoints

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/m',
        'user': '200/m',
        'emergency': '20/m',  # Stricter for emergency endpoints
    }
}

# views.py
from django_ratelimit.decorators import ratelimit

class EmergencyPublicView(APIView):
    permission_classes = [AllowAny]
    
    @ratelimit(key='ip', rate='20/m', method='GET', block=True)
    @ratelimit(key='qr_token', rate='50/m', method='GET', block=True)
    def get(self, request, qr_token):
        # Emergency access logic
        pass
```

### Claim PIN Security Flow

```python
# models.py
class Bracelet(models.Model):
    STATUS_CHOICES = [
        ('unclaimed', 'Unclaimed'),
        ('claimed', 'Claimed'),
        ('active', 'Active'),
        ('lost', 'Lost'),
    ]
    
    serial_number = models.CharField(max_length=50, unique=True)
    qr_token = models.UUIDField(unique=True)
    claim_pin = models.CharField(max_length=6, null=True)  # 6-digit PIN
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    profile = models.ForeignKey('profiles.MedicalProfile', null=True)
    ordered_at = models.DateTimeField(null=True)
    claimed_at = models.DateTimeField(null=True)

# views.py - Claim flow
class ClaimBraceletView(APIView):
    def post(self, request):
        serial = request.data.get('serial_number')
        pin = request.data.get('claim_pin')
        
        bracelet = Bracelet.objects.filter(serial_number=serial).first()
        
        if not bracelet:
            return Response({'error': 'Invalid serial'}, status=404)
        
        if bracelet.status != 'unclaimed':
            return Response({'error': 'Already claimed'}, status=400)
        
        # Verify PIN from packaging
        if bracelet.claim_pin != pin:
            return Response({'error': 'Invalid PIN'}, status=401)
        
        # Link to user's profile
        profile = request.user.medical_profile
        bracelet.profile = profile
        bracelet.status = 'active'
        bracelet.claimed_at = timezone.now()
        bracelet.save()
        
        return Response({'success': True})
```

### PWA Configuration for Offline Emergency Access

```typescript
// frontend/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  pwa: {
    dest: 'public',
    register: true,
    skipWaiting: true,
    disable: process.env.NODE_ENV === 'development',
    // Cache emergency UI for offline access
    runtimeCaching: [
      {
        urlPattern: /^https:\/\/api\.syra\.app\/e\/.*/,
        handler: 'NetworkFirst',
        options: {
          cacheName: 'emergency-api-cache',
          expiration: {
            maxEntries: 10,
            maxAgeSeconds: 300  // 5 minutes
          },
          networkTimeoutSeconds: 10
        }
      }
    ]
  }
}

module.exports = nextConfig
```

```json
// frontend/public/manifest.json
{
  "name": "SYRA Emergency",
  "short_name": "SYRA",
  "theme_color": "#E53935",
  "background_color": "#FFFFFF",
  "display": "standalone",
  "orientation": "portrait",
  "icons": [
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ]
}
```

### JSONB for Data Visibility

```python
# models.py
from django.contrib.postgres.fields import JSONField

class MedicalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # JSONB for flexible visibility
    allergies = JSONField(default=list)  # [{name, severity, visibility}]
    medications = JSONField(default=list)  # [{name, dosage, frequency, visibility}]
    conditions = JSONField(default=list)  # [{name, visibility}]
    emergency_contacts = JSONField(default=list)
    
    def get_visible_data(self, viewer_role: str) -> dict:
        """
        Filter data based on viewer role
        viewer_role: 'public' | 'medical' | 'owner'
        """
        def filter_by_visibility(items):
            return [
                item for item in items 
                if item.get('visibility') in [viewer_role, 'public', 'private']
                or (viewer_role == 'owner' or item.get('visibility') != 'private')
            ]
        
        return {
            'allergies': filter_by_visibility(self.allergies),
            'medications': filter_by_visibility(self.medications),
            'conditions': filter_by_visibility(self.conditions),
        }
```

---

## 🏗️ Domain-Driven Design (DDD) Folder Structure

Updated backend structure with DDD approach:

```
/syra_backend
  /core                        # Django project settings
    __init__.py
    settings/
      __init__.py
      base.py
      development.py
      production.py
    wsgi.py
    asgi.py
    urls.py
  
  /apps
    /accounts                 # User management, auth, JWT
      models.py
      views.py
      serializers.py
      urls.py
      managers.py
    
    /profiles                 # Medical profiles, visibility
      models.py
      views.py
      serializers.py
      signals.py              # Cache invalidation
      managers.py
    
    /emergency                # Public QR endpoints
      views.py
      middleware.py
      throttles.py
    
    /hardware                 # QR/NFC bracelet management
      models.py
      services.py             # QR generation, claim logic
      views.py
    
    /store                    # E-commerce, Stripe
      models.py
      views.py
      webhooks.py
      serializers.py
  
  /services                   # External integrations
    s3_service.py            # S3 presigned URLs
    redis_service.py          # Cache operations
    stripe_service.py         # Payment processing
    sms_service.py            # Twilio SMS
    audit_service.py          # Audit logging
  
  /api                        # DRF URL routing
    router.py
    urls.py
  
  /common                     # Shared utilities
    encryption.py
    validators.py
    constants.py

/frontend
  /app
    /(auth)/
    /dashboard/
    /e/[qr_id]/              # Emergency SSR page
    /shop/
  /components
  /lib
  /public                    # PWA assets
    manifest.json
    sw.js                    # Service worker
```

---

## 🌍 Egypt/ME Region Infrastructure

```python
# settings/production.py

# AWS ME-South-1 (Bahrain) for Egypt compliance
AWS_REGION = 'me-south-1'
AWS_S3_REGION_NAME = 'me-south-1'

# Or use local Egyptian cloud (e.g., Etisalat Cloud)
# CLOUD_PROVIDER = 'etisalat'

# Data residency
DATA_RESIDENCY = {
    'country': 'EG',
    'law': 'EG DPA 2020',
    'minimize_transfer': True,
}

# Local CDN for Egypt (reduce latency)
CDN_CONFIG = {
    'primary': 'https://cdn.syra.app',  # Cloudflare
    'fallback': 'https://cdn-eg.syra.app',  # Local cache
}
```

---

## 📦 QR Pre-generation Workflow

```python
# management/commands/generate_qr_batch.py
from django.core.management.base import BaseCommand
from apps.hardware.models import Bracelet
import uuid

class Command(BaseCommand):
    help = 'Pre-generate unclaimed QR codes for manufacturing'
    
    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=1000)
    
    def handle(self, *args, **options):
        count = options['count']
        
        for i in range(count):
            serial = f'SYRA-{uuid.uuid4().hex[:8].upper()}'
            qr_token = uuid.uuid4()
            claim_pin = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            Bracelet.objects.create(
                serial_number=serial,
                qr_token=qr_token,
                claim_pin=claim_pin,
                status='unclaimed'
            )
        
        self.stdout.write(self.style.SUCCESS(f'Generated {count} QR codes'))
```

### Physical Bracelet Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                 Bracelet Manufacturing Flow                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. MANUFACTURING                                               │
│     ┌─────────────────────────────────────────────────────┐    │
│     │  Generate batch of QR codes → Print on bracelets    │    │
│     │  Include Claim PIN card in packaging                │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                  │
│  2. WAREHOUSE                                                   │
│     ┌─────────────────────────────────────────────────────┐    │
│     │  Bracelets in "unclaimed" status                    │    │
│     │  Serial numbers tracked in system                   │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                  │
│  3. PURCHASE                                                    │
│     ┌─────────────────────────────────────────────────────┐    │
│     │  Customer buys → Order created → Status: pending   │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                  │
│  4. DELIVERY                                                    │
│     ┌─────────────────────────────────────────────────────┐    │
│     │  Bracelet shipped → Status: shipped                 │    │
│     │  User receives package with Claim PIN               │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                  │
│  5. CLAIM (User Action)                                         │
│     ┌─────────────────────────────────────────────────────┐    │
│     │  Scan QR → Enter PIN → Profile linked               │    │
│     │  Status: active                                     │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Final Integration Checklist

Before launching, ensure:

- [ ] Django Ratelimit configured on all `/e/` and `/qr/` endpoints
- [ ] S3 buckets NOT public - all access via presigned URLs
- [ ] All medical access logged (public + medical personnel)
- [ ] Claim PIN flow implemented and tested
- [ ] QR batch pre-generation script ready for manufacturing
- [ ] PWA manifest configured for offline emergency access
- [ ] Redis cache invalidation via Django Signals
- [ ] JSONB visibility filtering working
- [ ] AWS ME-South-1 or local Egypt hosting configured
- [ ] EG DPA compliance verified

```python
# Audit logging middleware
class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if '/emergency/' in request.path:
            AuditLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                ip_address=self.get_client_ip(request),
                path=request.path,
                method=request.method,
                timestamp=timezone.now()
            )
        return self.get_response(request)
```

---

## 8. Monitoring Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                      Monitoring Setup                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Errors: Sentry                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  - Django exceptions                                        ││
│  │  - Next.js runtime errors                                   ││
│  │  - Performance monitoring                                   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Metrics: Prometheus + Grafana                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  - Redis hit/miss ratio (emergency endpoint perf)           ││
│  │  - API response times                                        ││
│  │  - QR scan count                                             ││
│  │  - Active users                                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Logs: ELK Stack                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  - Searchable audit logs                                     ││
│  │  - Error correlation                                         ││
│  └─────────────────────────────────────────────────────────────┘│
```

---

## 9. Monetization (Stripe Webhooks)

```python
# E-commerce webhooks
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import stripe

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        if event['type'] == 'customer.subscription.created':
            # Grant premium access
            user = User.objects.get(email=event['data']['object']['email'])
            user.subscription_type = 'premium'
            user.save()
            
        elif event['type'] == 'customer.subscription.deleted':
            # Revoke premium access
            pass
            
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    return HttpResponse(status=200)
```

---

## 10. MVP Phasing (4-Week Launch)

```
┌─────────────────────────────────────────────────────────────────┐
│                    MVP 4-Week Timeline                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  WEEK 1-2: Core Backend                                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  □ Django setup + PostgreSQL                                ││
│  │  □ User registration + JWT auth                            ││
│  │  □ Medical profile CRUD                                     ││
│  │  □ Emergency endpoint with Redis cache                     ││
│  │  □ Basic rate limiting                                      ││
│  │  ─────────────────────────────────────────────              ││
│  │  Deliverable: Working API with emergency access            ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  WEEK 3: Frontend + E-commerce                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  □ Next.js setup                                            ││
│  │  □ User dashboard                                            ││
│  │  □ Profile management                                        ││
│  │  □ Product listing + cart                                    ││
│  │  □ Stripe checkout                                           ││
│  │  ─────────────────────────────────────────────              ││
│  │  Deliverable: Working web app with shop                    ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  WEEK 4: Integration + Testing                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  □ QR code generation + printing                            ││
│  │  □ End-to-end QR scan testing                                ││
│  │  □ Emergency interface testing                              ││
│  │  □ Security hardening                                        ││
│  │  □ Deploy to Railway                                         ││
│  │  ─────────────────────────────────────────────              ││
│  │  Deliverable: Production-ready MVP                         ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. Egypt-Focused Considerations

### Local CDN
```python
# For Cairo/EG users, use local CDN (Arqam/Cloudflare)
# settings.py
CDN_URL = os.environ.get('CDN_URL', 'https://cdn.syra.app')

# Egypt Data Protection Act (EG DPA) compliance
DATA_PROTECTION = {
    'law': 'EG DPA 2020',  # Similar to GDPR
    'consent_required': True,
    'data_retention_years': 7,
}
```

### Localization
```python
# Egyptian Arabic support
LANGUAGE_CODE = 'ar-EG'
USE_I18N = True

# Currency
STRIPE_CURRENCY = 'egp'  # Egyptian Pound
```

---

## 12. Disaster Recovery Plan

### Backup Strategy

```python
# settings/production.py - Database backup configuration
DATABASE_BACKUP = {
    'SCHEDULE': 'daily',  # or 'hourly' for PHI
    'RETENTION_DAYS': 90,
    'ENCRYPTION': True,  # Encrypt backups before storage
    'CROSS_REGION': True,  # Replicate to secondary region
}
```

| Backup Type | Frequency | Retention | Storage |
|-------------|-----------|-----------|---------|
| Full Database | Daily | 90 days | S3 Cross-Region |
| Incremental | Hourly | 7 days | S3 Standard |
| Transaction Logs | Continuous | 24 hours | S3 Standard |
| File/Media | Daily | 30 days | S3 Standard |

### Failover Procedure

```
┌─────────────────────────────────────────────────────────────────┐
│                    Failover Decision Tree                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Alert Triggered                                                 │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────┐    No    ┌──────────────────┐                │
│  │ DB Down?    │──────────▶│ Check API Health │                │
│  └──────┬──────┘           └──────────────────┘                │
│         │ Yes                                                     │
│         ▼                                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. Promote Read Replica to Primary                       │   │
│  │ 2. Update DNS to point to new primary                    │   │
│  │ 3. Enable Redis failover (if cluster)                    │   │
│  │ 4. Notify via PagerDuty                                   │   │
│  │ 5. Document incident                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Recovery Time Objectives

| Component | RTO (Recovery Time) | RPO (Recovery Point) |
|-----------|--------------------|--------------------|
| Database | < 15 minutes | < 1 hour |
| Redis Cache | < 5 minutes | N/A (cache rebuilds) |
| Application | < 10 minutes | N/A |
| Static Assets | < 5 minutes | N/A (CDN) |

### Emergency Contact Protocol

```python
# Emergency contacts for on-call team
ON_CALL_CONFIG = {
    'pagerduty_key': os.environ.get('PAGERDUTY_KEY'),
    'escalation_timeout_minutes': 15,
    'backup_contacts': [
        {'role': 'CTO', 'phone': '+20xxxxxxxxx'},
        {'role': 'Lead Engineer', 'phone': '+20xxxxxxxxx'},
    ]
}
```

---

## 13. HIPAA Compliance Details

### Risk Assessment Framework

```python
# security/risk_assessment.py
class HIPAARiskAssessment:
    """
    Annual risk assessment requirements for HIPAA compliance
    """
    RISK_AREAS = [
        'electronic_phi_access',
        'data_transmission_security',
        'physical_access_controls',
        'workstation_security',
        'device_management',
        'incident_response',
        'business_associate_management',
    ]
    
    def assess(self) -> dict:
        """Conduct annual risk assessment"""
        return {
            'likelihood': 'low/medium/high',
            'impact': 'low/medium/high',
            'mitigation': 'description',
            'review_date': 'annual'
        }
```

### Minimum Necessary Access Controls

```python
# Access control based on role (minimum necessary principle)
class MinimumNecessaryAccess:
    """
    Users should only access PHI necessary for their role
    """
    ROLE_PERMISSIONS = {
        'owner': ['allergies', 'medications', 'conditions', 'emergency_contacts', 'blood_type'],
        'medical_personnel': ['allergies', 'medications', 'conditions', 'blood_type'],
        'emergency_public': ['allergies', 'blood_type', 'critical_conditions'],
        'no_access': [],
    }
```

### Breach Notification Procedure

```python
# security/breach_response.py
class BreachNotificationWorkflow:
    """
    HIPAA breach notification requirements (60 days)
    """
    NOTIFICATION_TIMELINE = {
        'individual_notification': 60,  # days
        'hipaa_通知': 60,  # days  
        'media_notification': 60,  # days (>500 records)
    }
    
    def report_breach(self, scope: int, phi_types: list):
        """
        If breach affects >500 individuals:
        - Notify affected individuals
        - Notify HHS OCR
        - Media notification if major incident
        """
        if scope > 500:
            self.notify_hhs_ocr()
            self.notify_media()
        else:
            self.log_for_annual_reporting()
```

### Workforce Training Requirements

| Training Type | Frequency | Audience |
|---------------|-----------|----------|
| HIPAA Basics | Annual | All employees |
| PHI Handling | Annual | Access PHI |
| Security Awareness | Quarterly | All employees |
| Incident Response | Annual | IT/Engineering |

---

## 14. Error Handling & Graceful Degradation

### Redis Failure Fallback

```python
# services/cache_fallback.py
class CacheFallbackService:
    """
    Graceful degradation when Redis is unavailable
    """
    def get_emergency_data(self, qr_token: str):
        try:
            # Primary: Redis cache
            return redis.get(f'qr:{qr_token}:critical')
        except redis.ConnectionError:
            # Fallback 1: Serve stale cache (if available)
            stale = redis.get(f'qr:{qr_token}:critical:stale')
            if stale:
                log.warning(f'Serving stale cache for {qr_token}')
                return stale
            # Fallback 2: Direct database query
            return self.get_from_database(qr_token)
    
    def get_from_database(self, qr_token: str):
        """Direct DB query - slower but available"""
        profile = MedicalProfile.objects.filter(
            qr_token=qr_token, is_active=True
        ).values('allergies', 'blood_type', 'critical_conditions')
        return profile
```

### Circuit Breaker Pattern

```python
# services/circuit_breaker.py
from django.core.cache import cache

class CircuitBreaker:
    """
    Prevent cascading failures by opening circuit on external services
    """
    def __init__(self, service_name: str, failure_threshold: int = 5):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.failure_count = 0
        self.circuit_open = False
    
    def call(self, func, *args, **kwargs):
        if self.circuit_open:
            return self.fallback(func.__name__)
        
        try:
            result = func(*args, **kwargs)
            self.failure_count = 0  # Reset on success
            return result
        except Exception as e:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.circuit_open = True
                log.critical(f'Circuit OPEN for {self.service_name}')
            return self.fallback(func.__name__)
    
    def fallback(self, func_name):
        """Return degraded service response"""
        return {'status': 'degraded', 'service': self.service_name}
```

### Error Response Standards

```python
# api/error_handlers.py
ERROR_RESPONSES = {
    'rate_limit_exceeded': {
        'error': 'rate_limit_exceeded',
        'message': 'Too many requests. Please try again later.',
        'retry_after': 60
    },
    'qr_not_found': {
        'error': 'qr_not_found',
        'message': 'Invalid or expired QR code.'
    },
    'emergency_unavailable': {
        'error': 'service_unavailable',
        'message': 'Emergency service temporarily degraded. Contact emergency services directly.',
        'code': 'CALL_EMERGENCY'
    }
}
```

---

## 15. Enhanced Monitoring & Uptime

### Synthetic Monitoring for Emergency Endpoint

```yaml
# .github/workflows/synthetic-tests.yml
name: Emergency Endpoint Health Checks
on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test emergency endpoint
        run: |
          response=$(curl -s -o /dev/null -w "%{http_code}" \
            https://api.syra.app/e/TEST-UUID/critical/)
          if [ "$response" != "200" ]; then
            curl -X POST $PAGERDUTY_WEBHOOK -d '{"event":"trigger","service":"emergency-api"}'
          fi
```

### Comprehensive Monitoring Stack

| Tool | Purpose | Alert Threshold |
|------|---------|------------------|
| Sentry | Error tracking + performance | Any error |
| Prometheus | Custom metrics | CPU > 80%, Memory > 85% |
| Grafana | Dashboards | N/A |
| PagerDuty | On-call escalation | Critical only |
| UptimeRobot | HTTP uptime | Any downtime |
| CloudWatch | AWS resources | Auto-scaling events |

### Key Metrics Dashboard

```python
# monitoring/dashboards.py
DASHBOARD_METRICS = {
    'emergency_endpoint': [
        'response_time_p95',  # Target: < 100ms
        'response_time_p99',
        'cache_hit_ratio',   # Target: > 95%
        'requests_per_minute',
    ],
    'authentication': [
        'failed_login_attempts',
        'token_refresh_rate',
        'mfa_usage_percentage',
    ],
    'business': [
        'active_users',
        'qr_scans_daily',
        'bracelets_claimed',
        'subscription_conversion',
    ]
}
```

---

## 16. Data Migration Strategy (SQLite → PostgreSQL)

### Pre-Migration Checklist

```bash
# 1. Audit current data
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> print(f"Users: {User.objects.count()}")

# 2. Install PostgreSQL
docker run -d -e POSTGRES_PASSWORD=secret -p 5432:5432 postgres:15

# 3. Install database
pip install psycopg2-binary
```

### Migration Commands

```bash
# Using django-pg-zero-downtime
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'syra_prod',
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}

# Migration with no data loss
python manage.py migrate --database=default

# If using pgloader (faster for large datasets)
# migration.sql
LOAD DATABASE
     FROM sqlite:///db.sqlite3
     INTO postgresql://user:pass@localhost/syra_prod
WITH include no data,
     create tables,
     create indexes,
     reset sequences;
```

### Post-Migration Verification

```python
# management/commands/verify_migration.py
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        
        # Verify user count matches
        sqlite_count = 0  # From pre-migration audit
        pg_count = User.objects.count()
        
        if sqlite_count != pg_count:
            self.stderr.write(f'MISMATCH: {sqlite_count} vs {pg_count}')
        else:
            self.stdout.write(self.style.SUCCESS('Migration verified'))
        
        # Verify critical data integrity
        profiles = MedicalProfile.objects.count()
        self.stdout.write(f'Medical profiles: {profiles}')
```

---

## 17. Vendor Security Assessment

### Third-Party Security Requirements

```python
# security/vendor_assessment.py
VENDOR_REQUIREMENTS = {
    'cloud_provider': {
        'required': ['HIPAA BAA', 'SOC 2 Type II', 'ISO 27001'],
        'review_frequency': 'annual',
    },
    'payment_processor': {
        'required': ['PCI DSS Level 1', 'SOC 2'],
        'data_handling': 'tokenized_only',  # Never store card data
    },
    'sms_provider': {
        'required': ['HIPAA BAA', 'encryption_at_rest'],
        'phi_allowed': False,  # No PHI in SMS
    },
    'cdn_provider': {
        'required': ['WAF', 'DDoS protection'],
        'phi_allowed': False,  # No PHI via CDN
    }
}
```

---

## 18. Mandatory QR Rotation Feature

```python
# apps/qr/services.py
class QRRotationService:
    """
    Allow users to regenerate QR code if compromised
    Invalidates old QR token immediately
    """
    def rotate_qr(self, user, reason: str = 'user_requested'):
        profile = user.medical_profile
        
        # Generate new token
        new_token = uuid.uuid4()
        old_token = profile.qr_token
        
        # Update profile with new token
        profile.qr_token = new_token
        profile.qr_token_hash = hashlib.sha256(str(new_token).encode()).hexdigest()
        profile.save()
        
        # Invalidate old cache
        redis.delete(f'qr:{old_token}:critical')
        redis.delete(f'qr:{old_token}:extended')
        
        # Log rotation for audit
        QRRotationLog.objects.create(
            user=user,
            old_token_hash=hashlib.sha256(str(old_token).encode()).hexdigest()[:8],
            new_token_hash=hashlib.sha256(str(new_token).encode()).hexdigest()[:8],
            reason=reason,
            timestamp=timezone.now()
        )
        
        return new_token
```

```python
# QR rotation API endpoint
class QRRotateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        service = QRRotationService()
        new_token = service.rotate_qr(request.user, reason='user_requested')
        
        # Notify user
        send_email(
            subject='Your SYRA QR Code Has Been Rotated',
            template='qr_rotated',
            user=request.user
        )
        
        return Response({'success': True, 'qr_url': f'/e/{new_token}/'})
```

---

## 19. Adjusted Rate Limiting for Emergency Endpoints

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/m',
        'user': '200/m',
        'emergency': '50/m',  # Increased from 20 for mass casualty events
        'emergency_captcha': '200/m',  # After CAPTCHA verification
    }
}

# views.py - Add CAPTCHA fallback
class EmergencyPublicView(APIView):
    permission_classes = [AllowAny]
    
    @ratelimit(key='ip', rate='50/m', method='GET', block=True)
    def get(self, request, qr_token):
        # Check if rate limited, offer CAPTCHA
        if request.limited:
            return Response({
                'error': 'rate_limit_exceeded',
                'captcha_required': True,
                'captcha_url': '/api/captcha/generate/'
            }, status=429)
        
        return self.get_emergency_data(qr_token)
```

---

## ✅ Final Summary of Improvements

| Category | Original | Improved |
|----------|----------|----------|
| API Gateway | Kong/Generic | Django routing (MVP) |
| Rate Limiting | 20 req/min | 50 req/min + CAPTCHA fallback |
| Doctor Verification | Custom flow | Twilio Verify / reCAPTCHA |
| Architecture | Microservices-ready | BFF pattern (MVP) |
| Deployment | AWS EKS from start | Railway → AWS ECS → EKS |
| Monitoring | Basic | Sentry + Prometheus + Grafana + UptimeRobot |
| Security | Basic | OWASP + SOC 2 prep + Audit logs |
| HIPAA | Mentioned only | Full compliance framework |
| Disaster Recovery | None | Full backup/failover strategy |
| Error Handling | None | Circuit breaker + fallback |
| QR Rotation | Optional | Mandatory feature |
| Timeline | 10 weeks | 4 weeks MVP |

The improved architecture is now **MVP-focused** while remaining **production-ready** for scale and HIPAA compliant.
