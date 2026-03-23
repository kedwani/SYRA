"""Models for the Profiles app - Medical profiles, medications, emergency contacts."""

import uuid
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from datetime import timedelta


class MedicalProfile(models.Model):
    """
    Core medical profile for a patient.
    Linked to a SyraUser with a unique public_id for emergency scanning.
    """

    BLOOD_TYPE_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
        ("Unknown", "Unknown"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="medical_profile",
    )
    public_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        db_index=True,
        editable=False,
        help_text="Unique UUID for NFC/QR scanning",
    )
    blood_type = models.CharField(
        max_length=10, choices=BLOOD_TYPE_CHOICES, default="Unknown"
    )
    chronic_diseases = models.TextField(
        blank=True,
        verbose_name="Chronic Diseases",
        help_text="List of chronic conditions (e.g., Diabetes, Hypertension)",
    )
    allergies = models.TextField(
        blank=True, verbose_name="Allergies", help_text="Known allergies"
    )
    emergency_notes = models.TextField(
        blank=True,
        verbose_name="Emergency Notes",
        help_text="Critical medical notes for first responders",
    )
    insurance_provider = models.CharField(
        max_length=200, blank=True, verbose_name="Insurance Provider"
    )
    insurance_number = models.CharField(
        max_length=50, blank=True, verbose_name="Insurance Number"
    )
    insurance_image = models.ImageField(
        upload_to="insurance/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "pdf"])],
        verbose_name="Insurance Card Image",
    )
    height = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Height (cm)"
    )
    weight = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Weight (kg)"
    )
    premium_access_logging = models.BooleanField(
        default=False,
        verbose_name="Access Log Tracking (Premium)",
        help_text="Track who views your profile. Requires premium subscription.",
    )

    # Visibility Controls - User controls which sections are public vs doctor-only
    show_blood_type_public = models.BooleanField(
        default=True,
        verbose_name="Show Blood Type to Public",
        help_text="Everyone can see blood type in emergencies",
    )
    show_allergies_public = models.BooleanField(
        default=True,
        verbose_name="Show Allergies to Public",
        help_text="Everyone can see allergies in emergencies",
    )
    show_medications_public = models.BooleanField(
        default=True,
        verbose_name="Show Medications to Public",
        help_text="Anyone can view medications in emergencies",
    )
    show_contacts_public = models.BooleanField(
        default=True,
        verbose_name="Show Emergency Contacts to Public",
        help_text="Anyone can view emergency contacts",
    )
    show_physical_public = models.BooleanField(
        default=False,
        verbose_name="Show Physical Info to Public",
        help_text="Anyone can view height/weight (doctors only by default)",
    )
    show_history_public = models.BooleanField(
        default=True,
        verbose_name="Show Medical History to Public",
        help_text="Anyone can view medical history (doctors only by default)",
    )
    show_chronic_diseases_public = models.BooleanField(
        default=True,
        verbose_name="Show Chronic Diseases to Public",
        help_text="Everyone can see chronic diseases in emergencies",
    )
    show_notes_public = models.BooleanField(
        default=True,
        verbose_name="Show Emergency Notes to Public",
        help_text="Everyone can see emergency notes in emergencies",
    )
    show_insurance_public = models.BooleanField(
        default=False,
        verbose_name="Show Insurance to Public",
        help_text="Anyone can view insurance info (doctors only by default)",
    )
    show_personal_public = models.BooleanField(
        default=True,
        verbose_name="Show Personal Details to Public",
        help_text="Everyone can see personal details in emergencies",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Medical Profile"
        verbose_name_plural = "Medical Profiles"
        indexes = [
            models.Index(fields=["user", "updated_at"]),
            models.Index(fields=["public_id"]),
        ]

    def __str__(self):
        return f"Medical Profile - {self.user.username}"

    def save(self, *args, **kwargs):
        """Encrypt insurance image before saving."""
        # Check if we have a file to encrypt
        if self.insurance_image:
            # Only encrypt if not already encrypted
            if not self._is_encrypted():
                self._encrypt_insurance_image()

        super().save(*args, **kwargs)

    def _is_encrypted(self):
        """Check if insurance image is already encrypted."""
        if not self.insurance_image:
            return False
        try:
            self.insurance_image.open()
            header = self.insurance_image.read(10)
            self.insurance_image.seek(0)
            self.insurance_image.close()
            return header.startswith(b"gAAAAAB")
        except Exception:
            return False

    def _encrypt_insurance_image(self):
        """Encrypt the insurance image."""
        if not self.insurance_image:
            return

        from django.core.files.base import ContentFile
        from cryptography.fernet import Fernet

        fernet_key = settings.FERNET_KEY.encode() if settings.FERNET_KEY else None
        if not fernet_key:
            return

        try:
            f = Fernet(fernet_key)

            # Read the image data - handle case where file might be closed
            try:
                # First try normal open with context manager
                with self.insurance_image.open() as image_file:
                    image_data = image_file.read()
            except ValueError:
                # Handle case where file is closed - try to reopen from storage
                self.insurance_image.open(mode="rb")
                image_data = self.insurance_image.read()
                self.insurance_image.close()

            # Encrypt the data
            encrypted_data = f.encrypt(image_data)

            # Store encrypted data - get current name before replacing
            current_name = self.insurance_image.name

            # Replace the file with encrypted content
            self.insurance_image.save(
                current_name, ContentFile(encrypted_data), save=False
            )
        except Exception as e:
            # Log error but don't crash - encryption is best-effort
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"Failed to encrypt insurance image for profile {self.pk}: {e}"
            )

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
        MedicalProfile, on_delete=models.CASCADE, related_name="medications"
    )
    name = models.CharField(max_length=200, verbose_name="Medication Name")
    dosage = models.CharField(
        max_length=100, verbose_name="Dosage", help_text="e.g., 500mg twice daily"
    )
    frequency = models.CharField(max_length=100, blank=True, verbose_name="Frequency")
    # Period in days - null means ongoing/long-term medication
    period_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Treatment Duration (days)",
        help_text="Number of days this medication should be taken. Leave empty for ongoing medications.",
    )
    notes = models.TextField(blank=True, verbose_name="Additional Notes")

    # Doctor-added tracking fields
    added_by_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="added_medications",
        verbose_name="Added by Doctor",
    )
    pending_approval = models.BooleanField(
        default=False,
        verbose_name="Pending User Approval",
        help_text="Medication added by doctor, awaiting user approval",
    )
    is_approved = models.BooleanField(
        default=True,
        verbose_name="Approved",
        help_text="Medication is approved and visible",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Medication"
        verbose_name_plural = "Medications"

    def __str__(self):
        return f"{self.name} - {self.dosage}"

    @property
    def is_active(self):
        """
        Calculate if medication is still active based on creation date and treatment period.
        - If period_days is None, medication is considered ongoing (active)
        - If period_days is set, check if we're still within the treatment period
        """
        if self.period_days is None:
            # No period specified - assume ongoing/long-term medication
            return True

        # Calculate end date
        end_date = self.created_at + timedelta(days=self.period_days)

        # Check if current date is before end date
        return timezone.now() < end_date

    @property
    def days_remaining(self):
        """
        Calculate days remaining in treatment period.
        Returns None if period is not set (ongoing medication).
        Returns 0 if treatment period has ended.
        Returns negative number if overdue.
        """
        if self.period_days is None:
            return None

        end_date = self.created_at + timedelta(days=self.period_days)
        remaining = (end_date - timezone.now()).days
        return max(0, remaining)


class EmergencyContact(models.Model):
    """Model for patient's emergency contacts (max 2)."""

    RELATIONSHIP_CHOICES = [
        ("spouse", "Spouse"),
        ("parent", "Parent"),
        ("sibling", "Sibling"),
        ("child", "Child"),
        ("friend", "Friend"),
        ("other", "Other"),
    ]

    profile = models.ForeignKey(
        MedicalProfile, on_delete=models.CASCADE, related_name="emergency_contacts"
    )
    name = models.CharField(max_length=200, verbose_name="Contact Name")
    relationship = models.CharField(
        max_length=20, choices=RELATIONSHIP_CHOICES, verbose_name="Relationship"
    )
    phone_number = models.CharField(max_length=15, verbose_name="Phone Number")
    alternate_phone = models.CharField(
        max_length=15, blank=True, verbose_name="Alternate Phone"
    )
    email = models.EmailField(
        blank=True,
        verbose_name="Email Address",
        help_text="Email for emergency notifications",
    )
    is_primary = models.BooleanField(default=False, verbose_name="Primary Contact")

    # Doctor-added tracking fields
    added_by_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="added_emergency_contacts",
        verbose_name="Added by Doctor",
    )
    pending_approval = models.BooleanField(
        default=False,
        verbose_name="Pending User Approval",
        help_text="Contact added by doctor, awaiting user approval",
    )
    is_approved = models.BooleanField(
        default=True,
        verbose_name="Approved",
        help_text="Contact is approved and visible",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Emergency Contact"
        verbose_name_plural = "Emergency Contacts"
        ordering = ["-is_primary", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_relationship_display()})"


class MedicalEvent(models.Model):
    """Model for tracking medical events/history."""

    EVENT_TYPE_CHOICES = [
        ("surgery", "Surgery"),
        ("hospitalization", "Hospitalization"),
        ("diagnosis", "Diagnosis"),
        ("emergency", "Emergency"),
        ("checkup", "Check-up"),
        ("other", "Other"),
    ]

    profile = models.ForeignKey(
        MedicalProfile, on_delete=models.CASCADE, related_name="medical_events"
    )
    event_type = models.CharField(
        max_length=20, choices=EVENT_TYPE_CHOICES, verbose_name="Event Type"
    )
    title = models.CharField(max_length=200, verbose_name="Title")
    description = models.TextField(blank=True, verbose_name="Description")
    date = models.DateField(verbose_name="Event Date")
    hospital_name = models.CharField(
        max_length=200, blank=True, verbose_name="Hospital/Clinic Name"
    )
    doctor_name = models.CharField(
        max_length=200, blank=True, verbose_name="Doctor Name"
    )

    # Doctor-added tracking fields
    added_by_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="added_medical_events",
        verbose_name="Added by Doctor",
    )
    pending_approval = models.BooleanField(
        default=False,
        verbose_name="Pending User Approval",
        help_text="Event added by doctor, awaiting user approval",
    )
    is_approved = models.BooleanField(
        default=True,
        verbose_name="Approved",
        help_text="Event is approved and visible",
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Approved At",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Medical Event"
        verbose_name_plural = "Medical Events"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.title} - {self.date}"


class ProfileAccessLog(models.Model):
    """
    Track who accessed medical profiles and when.
    Used for audit logging and paid feature tracking.
    """

    profile = models.ForeignKey(
        MedicalProfile, on_delete=models.CASCADE, related_name="access_logs"
    )
    accessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profile_access_logs",
    )
    access_role = models.CharField(max_length=20)
    access_type = models.CharField(
        max_length=20,
        choices=[
            ("emergency", "Emergency Scan"),
            ("emergency_alert", "Emergency Alert"),
            ("api", "API Access"),
            ("dashboard", "Dashboard View"),
        ],
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    accessed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profile Access Log"
        verbose_name_plural = "Profile Access Logs"
        ordering = ["-accessed_at"]

    def __str__(self):
        return f"{self.profile.user.username} - {self.accessed_at}"
