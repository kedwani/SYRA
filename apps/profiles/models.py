"""
Medical Profile model for SYRA.
Links user accounts to QR codes and manages visibility settings.
"""

import uuid
import hashlib
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class MedicalProfile(models.Model):
    """
    Medical profile linked to a QR code for emergency access.
    """
    
    # Visibility levels
    VISIBILITY_PUBLIC = 'public'
    VISIBILITY_MEDICAL = 'medical'
    VISIBILITY_PRIVATE = 'private'
    
    VISIBILITY_CHOICES = [
        (VISIBILITY_PUBLIC, 'Public - Anyone'),
        (VISIBILITY_MEDICAL, 'Medical Personnel Only'),
        (VISIBILITY_PRIVATE, 'Private - Owner Only'),
    ]
    
    # UUID primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # User relationship
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medical_profile',
        verbose_name=_('user')
    )
    
    # QR Token - UUID for URL-safe access
    qr_token = models.UUIDField(
        unique=True,
        db_index=True,
        verbose_name=_('QR token')
    )
    
    # QR Token Hash - for URL-friendly codes (Base64)
    qr_token_hash = models.CharField(
        max_length=128,
        unique=True,
        db_index=True,
        verbose_name=_('QR token hash')
    )
    
    # Profile visibility settings
    default_visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_PUBLIC,
        verbose_name=_('default visibility')
    )
    
    # Profile status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('is active')
    )
    
    # Emergency note - displayed prominently
    emergency_note = models.TextField(
        blank=True,
        verbose_name=_('emergency note')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Last accessed (for audit)
    last_accessed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('last accessed at')
    )
    
    class Meta:
        verbose_name = _('medical profile')
        verbose_name_plural = _('medical profiles')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Profile for {self.user.get_full_name() or self.user.username}"
    
    def save(self, *args, **kwargs):
        """Generate QR token hash on save."""
        if not self.qr_token_hash and self.qr_token:
            self.qr_token_hash = self._generate_hash(self.qr_token)
        super().save(*args, **kwargs)
    
    def _generate_hash(self, token: uuid.UUID) -> str:
        """Generate URL-safe hash from UUID."""
        # Use UUID4 format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
        # Convert to base64 URL-safe
        return hashlib.sha256(str(token).encode()).hexdigest()[:32]
    
    def get_qr_url(self, base_url: str = '') -> str:
        """Get the emergency access URL for this profile."""
        return f"{base_url}/e/{self.qr_token_hash}"
    
    def get_critical_data(self) -> dict:
        """
        Get critical emergency data for quick access.
        This includes: blood type, allergies, critical conditions.
        """
        from apps.medical.models import Allergy, Medication, Condition
        
        # Get user data
        user = self.user
        
        # Get visible allergies (severity: severe/life threatening)
        allergies = Allergy.objects.filter(
            profile=self,
            severity__in=['severe', 'life_threatening']
        ).values('name', 'severity')
        
        # Get critical conditions
        conditions = Condition.objects.filter(
            profile=self,
            severity__in=['severe', 'life_threatening']
        ).values('name', 'severity')
        
        return {
            'blood_type': user.blood_type,
            'allergies': list(allergies),
            'critical_conditions': list(conditions),
            'emergency_note': self.emergency_note,
            'last_updated': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def get_extended_data(self, viewer_role: str = 'public') -> dict:
        """
        Get extended medical data based on viewer role.
        
        Args:
            viewer_role: 'public', 'medical', or 'owner'
        """
        from apps.medical.models import Allergy, Medication, Condition, EmergencyContact
        
        def filter_by_visibility(items):
            if viewer_role == 'owner':
                return items
            return items.exclude(visibility=self.VISIBILITY_PRIVATE)
        
        return {
            'profile': {
                'full_name': self.user.get_full_name(),
                'date_of_birth': self.user.date_of_birth.isoformat() if self.user.date_of_birth else None,
                'blood_type': self.user.blood_type,
            },
            'allergies': list(filter_by_visibility(
                Allergy.objects.filter(profile=self)
            ).values('name', 'severity', 'visibility')),
            'medications': list(filter_by_visibility(
                Medication.objects.filter(profile=self)
            ).values('name', 'dosage', 'frequency', 'visibility')),
            'conditions': list(filter_by_visibility(
                Condition.objects.filter(profile=self)
            ).values('name', 'severity', 'visibility')),
            'emergency_contacts': list(
                EmergencyContact.objects.filter(profile=self).values(
                    'name', 'relationship', 'phone', 'email'
                )
            ),
            'emergency_note': self.emergency_note,
            'last_updated': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def create_for_user(cls, user) -> 'MedicalProfile':
        """Create a medical profile for a user."""
        profile = cls.objects.create(
            user=user,
            qr_token=uuid.uuid4(),
        )
        return profile