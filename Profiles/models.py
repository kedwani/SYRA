"""Models for the Profiles app - Medical profiles, medications, emergency contacts."""
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator


class MedicalProfile(models.Model):
    """
    Core medical profile for a patient.
    Linked to a SyraUser with a unique public_id for emergency scanning.
    """
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('Unknown', 'Unknown'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medical_profile'
    )
    public_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique UUID for NFC/QR scanning'
    )
    blood_type = models.CharField(
        max_length=10,
        choices=BLOOD_TYPE_CHOICES,
        default='Unknown'
    )
    chronic_diseases = models.TextField(
        blank=True,
        verbose_name='Chronic Diseases',
        help_text='List of chronic conditions (e.g., Diabetes, Hypertension)'
    )
    allergies = models.TextField(
        blank=True,
        verbose_name='Allergies',
        help_text='Known allergies'
    )
    emergency_notes = models.TextField(
        blank=True,
        verbose_name='Emergency Notes',
        help_text='Critical medical notes for first responders'
    )
    insurance_provider = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Insurance Provider'
    )
    insurance_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Insurance Number'
    )
    insurance_image = models.ImageField(
        upload_to='insurance/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'pdf'])],
        verbose_name='Insurance Card Image'
    )
    height = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Height (cm)'
    )
    weight = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Weight (kg)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Medical Profile'
        verbose_name_plural = 'Medical Profiles'

    def __str__(self):
        return f"Medical Profile - {self.user.username}"
    
    def save(self, *args, **kwargs):
        """Encrypt insurance image before saving."""
        if self.insurance_image:
            # Only encrypt if not already encrypted (check for Fernet header)
            self.insurance_image.open()
            header = self.insurance_image.read(10)
            self.insurance_image.seek(0)
            
            # If header starts with Fernet magic bytes, it's already encrypted
            if not header.startswith(b'gAAAAAB'):
                from django.core.files.base import ContentFile
                import base64
                from cryptography.fernet import Fernet
                
                # Get Fernet key from settings, ensure it's bytes
                fernet_key = settings.FERNET_KEY.encode() if settings.FERNET_KEY else None
                if fernet_key:
                    f = Fernet(fernet_key)
                    
                    # Read the image file
                    image_data = self.insurance_image.read()
                    self.insurance_image.close()
                    
                    # Encrypt the data
                    encrypted_data = f.encrypt(image_data)
                    
                    # Store encrypted data back
                    self.insurance_image.save(
                        self.insurance_image.name,
                        ContentFile(encrypted_data),
                        save=False
                    )
                else:
                    self.insurance_image.close()
            else:
                self.insurance_image.close()
        
        super().save(*args, **kwargs)

    def get_insurance_image_url(self):
        """Return decrypted image URL for authorized access."""
        if not self.insurance_image:
            return None
        
        # This would need a custom view to serve decrypted images
        # For now, return the encrypted file path
        return self.insurance_image.url


class Medication(models.Model):
    """Model for patient's active medications."""
    profile = models.ForeignKey(
        MedicalProfile,
        on_delete=models.CASCADE,
        related_name='medications'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Medication Name'
    )
    dosage = models.CharField(
        max_length=100,
        verbose_name='Dosage',
        help_text='e.g., 500mg twice daily'
    )
    frequency = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Frequency'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Currently Taking'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Additional Notes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Medication'
        verbose_name_plural = 'Medications'

    def __str__(self):
        return f"{self.name} - {self.dosage}"


class EmergencyContact(models.Model):
    """Model for patient's emergency contacts (max 2)."""
    RELATIONSHIP_CHOICES = [
        ('spouse', 'Spouse'),
        ('parent', 'Parent'),
        ('sibling', 'Sibling'),
        ('child', 'Child'),
        ('friend', 'Friend'),
        ('other', 'Other'),
    ]
    
    profile = models.ForeignKey(
        MedicalProfile,
        on_delete=models.CASCADE,
        related_name='emergency_contacts'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Contact Name'
    )
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        verbose_name='Relationship'
    )
    phone_number = models.CharField(
        max_length=15,
        verbose_name='Phone Number'
    )
    alternate_phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Alternate Phone'
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name='Primary Contact'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Emergency Contact'
        verbose_name_plural = 'Emergency Contacts'
        ordering = ['-is_primary', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_relationship_display()})"


class MedicalEvent(models.Model):
    """Model for tracking medical events/history."""
    EVENT_TYPE_CHOICES = [
        ('surgery', 'Surgery'),
        ('hospitalization', 'Hospitalization'),
        ('diagnosis', 'Diagnosis'),
        ('emergency', 'Emergency'),
        ('checkup', 'Check-up'),
        ('other', 'Other'),
    ]
    
    profile = models.ForeignKey(
        MedicalProfile,
        on_delete=models.CASCADE,
        related_name='medical_events'
    )
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        verbose_name='Event Type'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Title'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    date = models.DateField(
        verbose_name='Event Date'
    )
    hospital_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Hospital/Clinic Name'
    )
    doctor_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Doctor Name'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Medical Event'
        verbose_name_plural = 'Medical Events'
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - {self.date}"
