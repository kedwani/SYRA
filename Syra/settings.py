"""
Django settings for SYRA medical identification platform.
"""

import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# DEBUG must be defined first
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "syra.middleware": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        # Generate temporary key for development only
        SECRET_KEY = "django-insecure-dev-key-for-development-only-change-in-production"
    else:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY environment variable is required in production! "
            "Generate with: python -c 'import secrets; print(secrets.token_urlsafe(50))'"
        )

ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS", "localhost,127.0.0.1,testserver,syra.pythonanywhere.com"
).split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "tailwind",
    "accounts",
    "profiles",
    "store",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # i18n
    "syra.middleware.ForceLanguageMiddleware",  # Force language activation
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "syra.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "store.context_processors.cart_item_count",
            ],
        },
    },
]

WSGI_APPLICATION = "syra.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DB_NAME", str(BASE_DIR / "db.sqlite3")),
        # PostgreSQL options (used when DB_ENGINE is postgresql)
        "USER": os.environ.get("DB_USER", ""),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# For SQLite, add connection options for production use
if os.environ.get("DB_ENGINE") != "django.db.backends.postgresql":
    DATABASES["default"]["OPTIONS"] = {
        "timeout": 20,
    }

# Cache Configuration
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"

# Available languages
LANGUAGES = [
    ("en", "English"),
    ("ar", "العربية"),
]

# Language cookie and session settings for i18n
LANGUAGE_COOKIE_NAME = "django_language"
LANGUAGE_SESSION_KEY = "_language"

TIME_ZONE = "Africa/Cairo"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Locale paths for translations
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Additional directories where Django will look for static files during collectstatic
STATICFILES_DIRS = (
    [
        BASE_DIR / "static",
    ]
    if (BASE_DIR / "static").exists()
    else []
)

# Tailwind CSS Configuration
NPM_BIN_PATH = "npm"  # Path to npm executable

TAILWIND_APP_NAME = "theme"

TAILWIND_CONFIG = {
    "colors": {
        "medical": {
            "primary": "#1d4ed8",
            "primaryDark": "#1e40af",
            "primaryLight": "#3b82f6",
            "accent": "#14b8a6",
            "accentLight": "#2dd4bf",
            "emergency": "#dc2626",
            "emergencyDark": "#b91c1c",
            "emergencyLight": "#ef4444",
            "neutral": "#6b7280",
        },
        "success": "#16a34a",
        "warning": "#f59e0b",
        "danger": "#dc2626",
        "info": "#3b82f6",
    },
    "fontFamily": {
        "sans": ["Inter", "system-ui", "sans-serif"],
        "mono": ["JetBrains Mono", "monospace"],
    },
    "extend": {
        "animation": {
            "pulse-fast": "pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite",
            "pulse-slow": "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
            "slide-up": "slideUp 0.3s ease-out",
            "fade-in": "fadeIn 0.2s ease-out",
        },
        "keyframes": {
            "slideUp": {
                "0%": {"transform": "translateY(10px)", "opacity": "0"},
                "100%": {"transform": "translateY(0)", "opacity": "1"},
            },
            "fadeIn": {
                "0%": {"opacity": "0"},
                "100%": {"opacity": "1"},
            },
        },
    },
}

# Experimental: Try to use pytailwindcss without Node.js
TAILWIND_USE_PY = True

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# API Keys
NINJAS_API_KEY = "3jIsUMFu3r2qh2ObQ62w4ISGO3R58v3SOEUdiDVI"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.SyraUser"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# drf-spectacular settings
SPECTACULAR_SETTINGS = {
    "TITLE": "SYRA Medical Identification API",
    "DESCRIPTION": "API for SYRA medical identification platform",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/",
}

from datetime import timedelta
from cryptography.fernet import Fernet

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

# Rate Limiting Configuration
RATELIMIT_USE_CACHE = "default"
RATELIMIT_DEFAULT = "5/m"  # Default rate limit
RATELIMIT_AUTH = "10/m"  # Auth endpoints
RATELIMIT_REGISTER = "3/h"  # Registration - very restrictive

# FERNET Encryption Key - CRITICAL for production security
FERNET_KEY = os.environ.get("FERNET_KEY")
if not FERNET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured(
            "FERNET_KEY is required in production! "
            "Generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
        )
    # For development, check if we have a persistent dev key file
    dev_key_file = BASE_DIR / ".dev_fernet_key"
    if dev_key_file.exists():
        FERNET_KEY = dev_key_file.read_text().strip()
    else:
        # Generate and save a proper dev key
        from cryptography.fernet import Fernet

        FERNET_KEY = Fernet.generate_key().decode()
        dev_key_file.write_text(FERNET_KEY)
        # Add to .gitignore if not already there
        gitignore_path = BASE_DIR / ".gitignore"
        if gitignore_path.exists():
            content = gitignore_path.read_text()
            if ".dev_fernet_key" not in content:
                gitignore_path.write_text(content + "\n.dev_fernet_key\n")

# Validate the key format
if FERNET_KEY:
    try:
        from cryptography.fernet import Fernet

        Fernet(FERNET_KEY.encode())
    except Exception as e:
        raise ImproperlyConfigured(f"Invalid FERNET_KEY format: {e}")

# Email Configuration
# Using console for development - Brevo available for production
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@syra.app")

# Brevo API Configuration (for future use)
BREVO_API_KEY = os.environ.get(
    "BREVO_API_KEY",
    "eyJhcGlfa2V5IjoieGtleXNpYi0zOGVmYWZhMzcwYWRiMGVmY2JiNWFjOGY1ZGJmYTJkNDlhY2YyYzZlN2JiYzNjOTk0MDY3YzZhMWIxZGNiYTgyLXNROU9WaElrZVNLU0tkRnkifQ==",
)

# CORS Configuration
CORS_ALLOW_CREDENTIALS = True
if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:19006",
        "http://127.0.0.1:3000",
    ]
else:
    CORS_ALLOWED_ORIGINS = os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        "https://syra-app.com,https://www.syra-app.com,https://syra.pythonanywhere.com",
    ).split(",")

# Security Headers for Production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
