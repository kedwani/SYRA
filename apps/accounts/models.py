"""
User model for SYRA.
Extends Django's AbstractUser with healthcare-specific fields.
"""

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.managers import UserManager


class User(AbstractUser):
    """
    Extended user model for SYRA healthcare platform.
    """
    
    # Use custom manager
    objects = UserManager()
    
    # Email is the login identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    # Blood type choices
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('UNKNOWN', 'Unknown'),
    ]
    
    # Subscription type
    SUBSCRIPTION_CHOICES = [
        ('free', 'Free'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    # UUID for primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Override email to make it unique (required for USERNAME_FIELD)
    email = models.EmailField(unique=True, verbose_name=_('email address'))
    
    # Additional fields
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('phone number'))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_('date of birth'))
    blood_type = models.CharField(
        max_length=10, 
        choices=BLOOD_TYPE_CHOICES, 
        default='UNKNOWN',
        verbose_name=_('blood type')
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default.png',
        blank=True,
        verbose_name=_('avatar')
    )
    
    # Medical personnel fields
    is_medical_personnel = models.BooleanField(
        default=False,
        verbose_name=_('is medical personnel')
    )
    medical_license_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('medical license number')
    )
    hospital_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('hospital name')
    )
    hospital_verified = models.BooleanField(
        default=False,
        verbose_name=_('hospital verified')
    )
    
    # Subscription
    subscription_type = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_CHOICES,
        default='free',
        verbose_name=_('subscription type')
    )
    subscription_end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('subscription end date')
    )
    
    # Privacy and consent
    agreed_to_terms = models.BooleanField(
        default=False,
        verbose_name=_('agreed to terms')
    )
    privacy_consent = models.BooleanField(
        default=False,
        verbose_name=_('privacy consent')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    @property
    def is_premium(self):
        if self.subscription_type == 'free':
            return False
        if self.subscription_end_date:
            from django.utils import timezone
            return self.subscription_end_date > timezone.now()
        return self.subscription_type in ['premium', 'enterprise']
    
    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.username