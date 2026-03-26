"""
Custom validators for SYRA.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    """
    Validate phone number format.
    Accepts international formats: +20XXXXXXXXX, 01XXXXXXXXX, etc.
    """
    if not value:
        return
    
    # Remove spaces and dashes
    cleaned = re.sub(r'[\s\-]', '', value)
    
    # Check for valid Egyptian phone number patterns
    patterns = [
        r'^(\+20|20|0)?1[0-9]{9}$',  # Egyptian mobile
        r'^\+[1-9]\d{1,14}$',  # International format
    ]
    
    if not any(re.match(pattern, cleaned) for pattern in patterns):
        raise ValidationError(
            _('Enter a valid phone number.'),
            code='invalid_phone',
        )


def validate_license_number(value):
    """
    Validate medical license number format.
    """
    if not value:
        return
    
    # Allow alphanumeric with hyphens, minimum 5 characters
    if not re.match(r'^[A-Za-z0-9\-]{5,50}$', value):
        raise ValidationError(
            _('Enter a valid license number (alphanumeric, 5-50 characters).'),
            code='invalid_license',
        )


def validate_serial_number(value):
    """
    Validate bracelet serial number format (SYRA-XXXXXXXX).
    """
    if not value:
        return
    
    if not re.match(r'^SYRA-[A-Z0-9]{8}$', value.upper()):
        raise ValidationError(
            _('Enter a valid serial number (format: SYRA-XXXXXXXX).'),
            code='invalid_serial',
        )


def validate_claim_pin(value):
    """
    Validate 6-digit PIN for bracelet claiming.
    """
    if not value:
        return
    
    if not re.match(r'^\d{6}$', value):
        raise ValidationError(
            _('Enter a valid 6-digit PIN.'),
            code='invalid_pin',
        )