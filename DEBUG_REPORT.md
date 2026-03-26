# SYRA Project - Comprehensive Debugging Report

## Executive Summary

This report documents all issues identified during a comprehensive debugging review of the SYRA Emergency Medical Bracelet System. The review covered Django settings, models, views, serializers, URL configurations, security vulnerabilities, and frontend code.

**Total Issues Found: 12**
- Critical: 3
- High: 4
- Medium: 3
- Low: 2

---

## Critical Issues

### 1. Security: Insecure Default Secret Keys
**File:** [`syra/settings.py:15`](syra/settings.py:15), [`syra/settings.py:116`](syra/settings.py:116)
**Severity:** CRITICAL
**Description:** Both `SECRET_KEY` and `JWT_SECRET_KEY` have insecure default values that will be used if environment variables are not set.
```python
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production')
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'django-insecure-dev-jwt-key')
```
**Impact:** If deployed without setting environment variables, the application will use predictable secret keys, compromising all cryptographic operations including JWT tokens, CSRF protection, and session security.
**Fix:** Remove default values and require environment variables to be set.

### 2. Security: DEBUG Mode Enabled in Production
**File:** [`syra/settings.py:16`](syra/settings.py:16)
**Severity:** CRITICAL
**Description:** `DEBUG = True` is hardcoded, which will expose sensitive information in production.
```python
DEBUG = True
```
**Impact:** Stack traces, SQL queries, and sensitive configuration will be exposed to users in production.
**Fix:** Use environment variable: `DEBUG = os.environ.get('DEBUG', 'False') == 'True'`

### 3. Security: Unrestricted Host Access
**File:** [`syra/settings.py:17`](syra/settings.py:17)
**Severity:** CRITICAL
**Description:** `ALLOWED_HOSTS = ['*']` allows requests from any host.
```python
ALLOWED_HOSTS = ['*']
```
**Impact:** Application vulnerable to HTTP Host header attacks.
**Fix:** Use environment variable: `ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')`

---

## High Severity Issues

### 4. Bug: Incorrect Cache Invalidation Key
**File:** [`apps/profiles/views.py:107`](apps/profiles/views.py:107)
**Severity:** HIGH
**Description:** Cache invalidation uses `qr_token` (UUID) instead of `qr_token_hash` (string hash).
```python
cache_service.invalidate_emergency_cache(str(profile.qr_token))  # Wrong
```
**Impact:** Cache will never be invalidated when QR code is rotated, causing stale emergency data to be served.
**Fix:** Change to `cache_service.invalidate_emergency_cache(profile.qr_token_hash)`

### 5. Bug: Missing Request Parameter in Viewer Role Detection
**File:** [`apps/emergency/views.py:157`](apps/emergency/views.py:157)
**Severity:** HIGH
**Description:** `_get_viewer_role` method tries to access `self.kwargs['qr_hash']` but APIView doesn't have kwargs.
```python
profile = MedicalProfile.objects.get(qr_token_hash=self.kwargs['qr_hash'])  # Wrong
```
**Impact:** Method will raise AttributeError, breaking extended emergency data access for authenticated users.
**Fix:** Pass `qr_hash` as parameter to `_get_viewer_role(self, request, qr_hash)`.

### 6. Bug: HTTP Method Mismatch in Medical Personnel Verify
**File:** [`apps/accounts/views.py:186`](apps/accounts/views.py:186)
**Severity:** HIGH
**Description:** Function decorated with `@api_view(['GET'])` but handles both GET and POST requests.
```python
@api_view(['GET'])  # Only allows GET
def medical_personnel_verify(request):
    if request.method == 'GET':
        # ...
    # POST logic here (never reached)
```
**Impact:** POST requests to update medical personnel info will return 405 Method Not Allowed.
**Fix:** Change decorator to `@api_view(['GET', 'POST'])`.

### 7. Bug: Duplicate Frequency Display Values
**File:** [`apps/medical/models.py:103-110`](apps/medical/models.py:103)
**Severity:** HIGH
**Description:** Two frequency choices have the same display value "Once daily".
```python
FREQUENCY_ONCE = 'once'  # Display: 'Once daily'
FREQUENCY_DAILY = 'daily'  # Display: 'Once daily'
```
**Impact:** Users cannot distinguish between "once daily" and "daily" options.
**Fix:** Change `FREQUENCY_ONCE` display to "Once" or `FREQUENCY_DAILY` to "Daily".

---

## Medium Severity Issues

### 8. Bug: Incorrect Tax Calculation
**File:** [`apps/store/views.py:116`](apps/store/views.py:116)
**Severity:** MEDIUM
**Description:** Tax calculation uses `int()` which truncates decimal values.
```python
tax = int((subtotal + shipping_cost) * 0.14)  # Truncates decimals
```
**Impact:** Tax amounts will be incorrectly rounded down, causing financial discrepancies.
**Fix:** Use `Decimal` for financial calculations: `tax = int(Decimal(subtotal + shipping_cost) * Decimal('0.14'))`

### 9. Bug: Misleading Payment Status Field
**File:** [`apps/store/models.py:218`](apps/store/models.py:218)
**Severity:** MEDIUM
**Description:** `payment_status` field uses `STATUS_CHOICES` which includes order statuses like "shipped", "delivered", etc.
```python
payment_status = models.CharField(
    max_length=20,
    choices=STATUS_CHOICES,  # Wrong choices
    default=STATUS_PENDING,
)
```
**Impact:** Payment status can be set to invalid values like "shipped" or "delivered".
**Fix:** Create separate `PAYMENT_STATUS_CHOICES` with appropriate values.

### 10. Bug: Visibility Filter Logic Error
**File:** [`apps/profiles/models.py:152`](apps/profiles/models.py:152)
**Severity:** MEDIUM
**Description:** `filter_by_visibility` function compares visibility field to constant incorrectly.
```python
def filter_by_visibility(items):
    if viewer_role == 'owner':
        return items
    return items.exclude(visibility=self.VISIBILITY_PRIVATE)  # Wrong comparison
```
**Impact:** Private items may not be properly filtered for non-owner viewers.
**Fix:** Change to `items.exclude(visibility='private')`.

---

## Low Severity Issues

### 11. Configuration: Unnecessary Dependency
**File:** [`requirements/base.txt:16`](requirements/base.txt:16)
**Severity:** LOW
**Description:** `djangorestframework-simplejwt` is included but project uses custom JWT implementation.
**Impact:** Unnecessary dependency increases attack surface and package size.
**Fix:** Remove `djangorestframework-simplejwt` from requirements.

### 12. Security: CORS Allow All Origins
**File:** [`syra/settings.py:122`](syra/settings.py:122)
**Severity:** LOW (Development only)
**Description:** `CORS_ALLOW_ALL_ORIGINS = True` allows requests from any origin.
```python
CORS_ALLOW_ALL_ORIGINS = True
```
**Impact:** In production, this would allow any website to make API requests.
**Fix:** Use environment variable and restrict to specific origins in production.

---

## Recommendations

### Immediate Actions (Critical)
1. Remove default values for `SECRET_KEY` and `JWT_SECRET_KEY`
2. Make `DEBUG` configurable via environment variable
3. Restrict `ALLOWED_HOSTS` to specific domains

### Short-term Fixes (High)
1. Fix cache invalidation key in QR code rotation
2. Fix viewer role detection in emergency views
3. Fix HTTP method decorator for medical personnel verify
4. Fix duplicate frequency display values

### Medium-term Improvements
1. Use `Decimal` for all financial calculations
2. Create proper payment status choices
3. Fix visibility filter logic
4. Remove unnecessary dependencies

### Security Hardening
1. Implement proper CORS configuration for production
2. Add rate limiting (currently disabled)
3. Enable HTTPS in production settings
4. Add security headers (HSTS, etc.)

---

## Testing Recommendations

1. **Unit Tests:** Add tests for all fixed bugs
2. **Integration Tests:** Test QR code rotation and cache invalidation
3. **Security Tests:** Verify JWT token handling and authentication
4. **Financial Tests:** Verify tax calculations with edge cases

---

## Conclusion

The SYRA project has several critical security vulnerabilities and bugs that should be addressed before production deployment. The most urgent issues are the insecure default secret keys and DEBUG mode being enabled. The identified bugs in cache invalidation, viewer role detection, and HTTP method handling will cause functional failures in production.

All issues are fixable with the provided recommendations. Implementing these fixes will significantly improve the security, reliability, and functionality of the application.
