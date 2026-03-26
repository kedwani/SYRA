"""
Medical data models for SYRA.
Manages allergies, medications, conditions, and emergency contacts.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Allergy(models.Model):
    """
    Allergy model for tracking patient allergies.
    """
    
    # Severity levels
    SEVERITY_MILD = 'mild'
    SEVERITY_MODERATE = 'moderate'
    SEVERITY_SEVERE = 'severe'
    SEVERITY_LIFE_THREATENING = 'life_threatening'
    
    SEVERITY_CHOICES = [
        (SEVERITY_MILD, 'Mild'),
        (SEVERITY_MODERATE, 'Moderate'),
        (SEVERITY_SEVERE, 'Severe'),
        (SEVERITY_LIFE_THREATENING, 'Life Threatening'),
    ]
    
    # Visibility levels
    VISIBILITY_PUBLIC = 'public'
    VISIBILITY_MEDICAL = 'medical'
    VISIBILITY_PRIVATE = 'private'
    
    VISIBILITY_CHOICES = [
        (VISIBILITY_PUBLIC, 'Public - Anyone'),
        (VISIBILITY_MEDICAL, 'Medical Personnel Only'),
        (VISIBILITY_PRIVATE, 'Private - Owner Only'),
    ]
    
    # Profile relationship
    profile = models.ForeignKey(
        'profiles.MedicalProfile',
        on_delete=models.CASCADE,
        related_name='allergies',
        verbose_name=_('medical profile')
    )
    
    # Allergy details
    name = models.CharField(max_length=200, verbose_name=_('allergen name'))
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default=SEVERITY_MODERATE,
        verbose_name=_('severity')
    )
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_PUBLIC,
        verbose_name=_('visibility')
    )
    
    # Additional notes
    notes = models.TextField(blank=True, verbose_name=_('notes'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('allergy')
        verbose_name_plural = _('allergies')
        ordering = ['-severity', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_severity_display()})"


class Medication(models.Model):
    """
    Medication model for tracking current medications.
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
    
    # Frequency choices
    FREQUENCY_ONCE = 'once'
    FREQUENCY_TWICE = 'twice'
    FREQUENCY_THREE = 'three_times'
    FREQUENCY_DAILY = 'daily'
    FREQUENCY_WEEKLY = 'weekly'
    FREQUENCY_AS_NEEDED = 'as_needed'
    
    FREQUENCY_CHOICES = [
        (FREQUENCY_ONCE, 'Once daily'),
        (FREQUENCY_TWICE, 'Twice daily'),
        (FREQUENCY_THREE, 'Three times daily'),
        (FREQUENCY_DAILY, 'Once daily'),
        (FREQUENCY_WEEKLY, 'Weekly'),
        (FREQUENCY_AS_NEEDED, 'As needed'),
    ]
    
    # Profile relationship
    profile = models.ForeignKey(
        'profiles.MedicalProfile',
        on_delete=models.CASCADE,
        related_name='medications',
        verbose_name=_('medical profile')
    )
    
    # Medication details
    name = models.CharField(max_length=200, verbose_name=_('medication name'))
    dosage = models.CharField(max_length=100, verbose_name=_('dosage'))
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default=FREQUENCY_DAILY,
        verbose_name=_('frequency')
    )
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_PUBLIC,
        verbose_name=_('visibility')
    )
    
    # Additional info
    prescribed_by = models.CharField(max_length=200, blank=True, verbose_name=_('prescribed by'))
    reason = models.CharField(max_length=200, blank=True, verbose_name=_('reason for taking'))
    is_active = models.BooleanField(default=True, verbose_name=_('is active'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('medication')
        verbose_name_plural = _('medications')
        ordering = ['-is_active', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.dosage}"


class Condition(models.Model):
    """
    Medical condition model for tracking health conditions.
    """
    
    # Severity levels
    SEVERITY_MILD = 'mild'
    SEVERITY_MODERATE = 'moderate'
    SEVERITY_SEVERE = 'severe'
    SEVERITY_LIFE_THREATENING = 'life_threatening'
    
    SEVERITY_CHOICES = [
        (SEVERITY_MILD, 'Mild'),
        (SEVERITY_MODERATE, 'Moderate'),
        (SEVERITY_SEVERE, 'Severe'),
        (SEVERITY_LIFE_THREATENING, 'Life Threatening'),
    ]
    
    # Visibility levels
    VISIBILITY_PUBLIC = 'public'
    VISIBILITY_MEDICAL = 'medical'
    VISIBILITY_PRIVATE = 'private'
    
    VISIBILITY_CHOICES = [
        (VISIBILITY_PUBLIC, 'Public - Anyone'),
        (VISIBILITY_MEDICAL, 'Medical Personnel Only'),
        (VISIBILITY_PRIVATE, 'Private - Owner Only'),
    ]
    
    # Profile relationship
    profile = models.ForeignKey(
        'profiles.MedicalProfile',
        on_delete=models.CASCADE,
        related_name='conditions',
        verbose_name=_('medical profile')
    )
    
    # Condition details
    name = models.CharField(max_length=200, verbose_name=_('condition name'))
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default=SEVERITY_MODERATE,
        verbose_name=_('severity')
    )
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_PUBLIC,
        verbose_name=_('visibility')
    )
    
    # Additional info
    diagnosed_date = models.DateField(null=True, blank=True, verbose_name=_('diagnosed date'))
    notes = models.TextField(blank=True, verbose_name=_('notes'))
    is_active = models.BooleanField(default=True, verbose_name=_('is active'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('condition')
        verbose_name_plural = _('conditions')
        ordering = ['-severity', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_severity_display()})"


class EmergencyContact(models.Model):
    """
    Emergency contact model for storing emergency contact information.
    """
    
    # Relationship types
    RELATIONSHIP_CHOICES = [
        ('spouse', 'Spouse'),
        ('parent', 'Parent'),
        ('child', 'Child'),
        ('sibling', 'Sibling'),
        ('friend', 'Friend'),
        ('other', 'Other'),
    ]
    
    # Profile relationship
    profile = models.ForeignKey(
        'profiles.MedicalProfile',
        on_delete=models.CASCADE,
        related_name='emergency_contacts',
        verbose_name=_('medical profile')
    )
    
    # Contact details
    name = models.CharField(max_length=200, verbose_name=_('contact name'))
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        default='other',
        verbose_name=_('relationship')
    )
    phone = models.CharField(max_length=20, verbose_name=_('phone number'))
    email = models.EmailField(blank=True, verbose_name=_('email'))
    is_primary = models.BooleanField(default=False, verbose_name=_('is primary contact'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('emergency contact')
        verbose_name_plural = _('emergency contacts')
        ordering = ['-is_primary', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_relationship_display()})"