"""
Custom user manager for SYRA.
Provides methods for creating users and superusers.
"""

from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Custom user manager for SYRA.
    Email is the unique identifier instead of username.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('Email is required')
        
        email = self.normalize_email(email)
        
        # Set username to email if not provided
        if 'username' not in extra_fields:
            extra_fields['username'] = email.split('@')[0]
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)
    
    def get_queryset(self):
        """Return queryset with custom filtering."""
        return super().get_queryset()
    
    def active(self):
        """Return only active users."""
        return self.filter(is_active=True)
    
    def medical_personnel(self):
        """Return only verified medical personnel."""
        return self.filter(is_medical_personnel=True, hospital_verified=True)
    
    def premium(self):
        """Return only premium subscribers."""
        return self.filter(subscription_type__in=['premium', 'enterprise'])