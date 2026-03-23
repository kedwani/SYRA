"""
Configuration Validator for SYRA Project.

Validates critical configuration on application startup to catch configuration
errors before they cause runtime failures.
"""

import logging

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

logger = logging.getLogger(__name__)


def validate_configuration():
    """
    Validate critical configuration on startup.
    Raises ImproperlyConfigured if critical issues found.
    """
    errors = []
    warnings = []

    # Check SECRET_KEY
    default_secret = "django-insecure-dev-key-for-development-only-change-in-production"
    if settings.SECRET_KEY == default_secret:
        if not settings.DEBUG:
            errors.append("SECRET_KEY must be changed in production")
        else:
            warnings.append("Using default SECRET_KEY in development")

    # Check FERNET_KEY
    if settings.FERNET_KEY:
        try:
            from cryptography.fernet import Fernet

            Fernet(settings.FERNET_KEY.encode())
        except Exception as e:
            errors.append(f"Invalid FERNET_KEY: {e}")
    else:
        if not settings.DEBUG:
            errors.append("FERNET_KEY is required in production")

    # Check EMAIL settings in production
    if not settings.DEBUG:
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            warnings.append("Email settings not configured - emails will not send")

    # Check CORS settings
    if not settings.DEBUG:
        if not getattr(settings, "CORS_ALLOWED_ORIGINS", None):
            warnings.append("CORS_ALLOWED_ORIGINS not configured")

    # Check database settings
    if not settings.DEBUG:
        db_engine = settings.DATABASES["default"]["ENGINE"]
        if "sqlite3" in db_engine:
            warnings.append("SQLite should not be used in production")

    # Log warnings
    for warning in warnings:
        logger.warning(f"Configuration warning: {warning}")

    # Raise errors
    if errors:
        error_msg = "Configuration errors found:\n" + "\n".join(
            f"- {e}" for e in errors
        )
        raise ImproperlyConfigured(error_msg)

    logger.info("Configuration validation passed")
