"""
Hardware models for SYRA.
Manages bracelets, QR codes, and serial numbers.
"""

import uuid
import random
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.common.validators import validate_serial_number, validate_claim_pin


class Bracelet(models.Model):
    """
    Physical bracelet model linked to user profiles.
    """
    
    # Status choices
    STATUS_UNCLAIMED = 'unclaimed'
    STATUS_CLAIMED = 'claimed'
    STATUS_ACTIVE = 'active'
    STATUS_LOST = 'lost'
    STATUS_SUSPENDED = 'suspended'
    
    STATUS_CHOICES = [
        (STATUS_UNCLAIMED, 'Unclaimed'),
        (STATUS_CLAIMED, 'Claimed'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_LOST, 'Lost'),
        (STATUS_SUSPENDED, 'Suspended'),
    ]
    
    # UUID for primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Serial number - format: SYRA-XXXXXXXX
    serial_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        validators=[validate_serial_number],
        verbose_name=_('serial number')
    )
    
    # QR Token - linked to MedicalProfile
    qr_token = models.UUIDField(
        unique=True,
        db_index=True,
        verbose_name=_('QR token')
    )
    
    # Claim PIN - 6 digits for claiming
    claim_pin = models.CharField(
        max_length=6,
        validators=[validate_claim_pin],
        verbose_name=_('claim PIN')
    )
    
    # Profile relationship (when claimed)
    profile = models.ForeignKey(
        'profiles.MedicalProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bracelets',
        verbose_name=_('medical profile')
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_UNCLAIMED,
        verbose_name=_('status')
    )
    
    # Timestamps
    ordered_at = models.DateTimeField(null=True, blank=True, verbose_name=_('ordered at'))
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name=_('shipped at'))
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name=_('delivered at'))
    claimed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('claimed at'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('bracelet')
        verbose_name_plural = _('bracelets')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Bracelet {self.serial_number} ({self.get_status_display()})"
    
    @classmethod
    def generate(cls, count: int = 1) -> list:
        """
        Generate unclaimed bracelets with serial numbers and claim PINs.
        
        Args:
            count: Number of bracelets to generate
            
        Returns:
            List of created Bracelet instances
        """
        bracelets = []
        for _ in range(count):
            serial = f"SYRA-{uuid.uuid4().hex[:8].upper()}"
            pin = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            bracelet = cls.objects.create(
                serial_number=serial,
                qr_token=uuid.uuid4(),
                claim_pin=pin,
                status=cls.STATUS_UNCLAIMED,
            )
            bracelets.append(bracelet)
        
        return bracelets
    
    def claim(self, profile) -> bool:
        """
        Claim this bracelet for a medical profile.
        
        Args:
            profile: MedicalProfile instance
            
        Returns:
            True if successful
        """
        if self.status != self.STATUS_UNCLAIMED:
            return False
        
        from django.utils import timezone
        
        self.profile = profile
        self.status = self.STATUS_CLAIMED
        self.claimed_at = timezone.now()
        self.save()
        
        # Update the profile's QR token to match the bracelet
        profile.qr_token = self.qr_token
        profile.save()
        
        return True
    
    def mark_active(self) -> bool:
        """Mark bracelet as active after initial claim."""
        if self.status != self.STATUS_CLAIMED:
            return False
        
        self.status = self.STATUS_ACTIVE
        self.save()
        return True
    
    def mark_lost(self) -> bool:
        """Mark bracelet as lost."""
        if self.status not in [self.STATUS_ACTIVE, self.STATUS_CLAIMED]:
            return False
        
        self.status = self.STATUS_LOST
        self.save()
        return True
    
    def suspend(self) -> bool:
        """Suspend bracelet (admin action)."""
        self.status = self.STATUS_SUSPENDED
        self.save()
        return True