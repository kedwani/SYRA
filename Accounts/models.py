"""Models for the Accounts app."""
import re
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


def validate_egyptian_national_id(value):
    """Validate Egyptian National ID - must be exactly 14 digits."""
    if not re.match(r'^\d{14}$', str(value)):
        raise ValidationError(
            'Egyptian National ID must be exactly 14 digits.',
            code='invalid_national_id'
        )


class SyraUser(AbstractUser):
    """
    Extended User model for SYRA.
    Includes 14-digit Egyptian National ID as primary identifier.
    """
    national_id = models.CharField(
        max_length=14,
        unique=True,
        validators=[validate_egyptian_national_id],
        verbose_name='Egyptian National ID',
        help_text='14-digit Egyptian National ID'
    )
    phone_number = models.CharField(
        max_length=11,
        blank=True,
        verbose_name='Phone Number'
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name='Date of Birth'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'SYRA User'
        verbose_name_plural = 'SYRA Users'

    def __str__(self):
        return f"{self.username} ({self.national_id})"
