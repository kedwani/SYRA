"""
Profiles/models.py
------------------
Core data models for the SYRA medical platform.

Models:
  - MedicalProfile   : The main patient record (linked 1-to-1 with SyraUser).
  - EmergencyContact : Up to 2 contacts per patient.
  - Medication       : Current medications with start date + duration.
  - MedicalEvent     : Historical events (accidents, fractures, bleeding, etc.).

Insurance card images are stored encrypted on disk via a custom
EncryptedImageField to satisfy the privacy requirement in the spec.
"""

import os
import uuid

from cryptography.fernet import Fernet
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models


# ---------------------------------------------------------------------------
# Helper: deterministic upload path keeps media organised by user
# ---------------------------------------------------------------------------


def insurance_upload_path(instance: "MedicalProfile", filename: str) -> str:
    """Store encrypted insurance files under a per-user subdirectory."""
    ext = os.path.splitext(filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}.enc"
    return f"insurance/{instance.user.username}/{unique_name}"


# ---------------------------------------------------------------------------
# Encryption helper (uses SYRA_ENCRYPTION_KEY from settings)
# ---------------------------------------------------------------------------


def _get_fernet() -> Fernet:
    """Instantiate a Fernet cipher from the project's secret key."""
    key = getattr(settings, "SYRA_ENCRYPTION_KEY", None)
    if not key:
        raise RuntimeError(
            "SYRA_ENCRYPTION_KEY is not set in settings. "
            'Run: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        )
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_file(raw_bytes: bytes) -> bytes:
    """Encrypt raw file bytes and return ciphertext."""
    return _get_fernet().encrypt(raw_bytes)


def decrypt_file(cipher_bytes: bytes) -> bytes:
    """Decrypt ciphertext and return original raw bytes."""
    return _get_fernet().decrypt(cipher_bytes)


# ---------------------------------------------------------------------------
# Choice constants
# ---------------------------------------------------------------------------


class BloodType(models.TextChoices):
    A_POS = "A+", "A+"
    A_NEG = "A-", "A-"
    B_POS = "B+", "B+"
    B_NEG = "B-", "B-"
    AB_POS = "AB+", "AB+"
    AB_NEG = "AB-", "AB-"
    O_POS = "O+", "O+"
    O_NEG = "O-", "O-"
    UNKNOWN = "Unknown", "Unknown"


class Gender(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    OTHER = "O", "Other / Prefer not to say"


class MedicalEventType(models.TextChoices):
    ACCIDENT = "Accident", "Accident"
    FRACTURE = "Fracture", "Fracture"
    BLEEDING = "Bleeding", "Bleeding"
    SURGERY = "Surgery", "Surgery"
    OTHER = "Other", "Other"


# ---------------------------------------------------------------------------
# MedicalProfile
# ---------------------------------------------------------------------------


class MedicalProfile(models.Model):
    """
    Central patient record. Created automatically via Django signal
    when a new SyraUser registers (see Profiles/signals.py).

    The insurance_card_image is stored in an encrypted form on disk.
    The raw field stores the path to the .enc file; decryption happens
    in the serializer / insurance-specific endpoint only.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="medical_profile",
    )

    # QR / NFC identifier — generated once, never changes
    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="Public QR/NFC ID",
    )

    # ---- Demographics ----
    blood_type = models.CharField(
        max_length=10,
        choices=BloodType.choices,
        default=BloodType.UNKNOWN,
    )
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    # ---- Insurance (sensitive — separated endpoint) ----
    insurance_company = models.CharField(max_length=120, blank=True)
    # Stores path to the *encrypted* image file on disk
    insurance_card_encrypted_path = models.CharField(
        max_length=512,
        blank=True,
        verbose_name="Encrypted Insurance Card Path",
    )

    # ---- Medical conditions ----
    chronic_diseases = models.TextField(
        blank=True,
        help_text="Comma-separated list, e.g. 'Diabetes Type 2, Hypertension'",
    )
    immune_diseases = models.TextField(
        blank=True,
        help_text="Immune / auto-immune conditions",
    )
    allergies = models.TextField(blank=True)

    # ---- General notes (doctor / patient free text) ----
    general_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Medical Profile"
        verbose_name_plural = "Medical Profiles"

    def __str__(self) -> str:
        return f"Profile of {self.user.username}"

    # ------------------------------------------------------------------
    # Insurance image encryption helpers
    # ------------------------------------------------------------------

    def save_encrypted_insurance_image(self, raw_image_file) -> None:
        """
        Accepts an uploaded InMemoryUploadedFile / file-like object,
        encrypts its content, then saves the ciphertext to media storage.
        Updates self.insurance_card_encrypted_path but does NOT call
        self.save() — callers should do that.
        """
        raw_bytes = raw_image_file.read()
        encrypted_bytes = encrypt_file(raw_bytes)

        relative_path = insurance_upload_path(self, raw_image_file.name)
        saved_path = default_storage.save(
            relative_path,
            ContentFile(encrypted_bytes),
        )
        self.insurance_card_encrypted_path = saved_path

    def get_decrypted_insurance_image(self) -> bytes:
        """
        Reads and decrypts the stored insurance card image.
        Returns raw bytes (caller decides how to serve them).
        Raises FileNotFoundError if no image has been stored.
        """
        if not self.insurance_card_encrypted_path:
            raise FileNotFoundError("No insurance card image on record.")

        with default_storage.open(self.insurance_card_encrypted_path, "rb") as f:
            cipher_bytes = f.read()

        return decrypt_file(cipher_bytes)


# ---------------------------------------------------------------------------
# EmergencyContact (max 2 per patient, enforced in serializer)
# ---------------------------------------------------------------------------


class EmergencyContact(models.Model):
    """
    Up to 2 emergency contacts per MedicalProfile.
    Priority 1 is contacted first.
    """

    profile = models.ForeignKey(
        MedicalProfile,
        on_delete=models.CASCADE,
        related_name="emergency_contacts",
    )
    name = models.CharField(max_length=120)
    relationship = models.CharField(max_length=60, blank=True)
    phone_number = models.CharField(max_length=20)
    priority = models.PositiveSmallIntegerField(
        default=1,
        help_text="1 = primary contact, 2 = secondary contact",
    )

    class Meta:
        ordering = ["priority"]
        verbose_name = "Emergency Contact"
        verbose_name_plural = "Emergency Contacts"
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "priority"],
                name="unique_priority_per_profile",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.relationship}) — Priority {self.priority}"


# ---------------------------------------------------------------------------
# Medication
# ---------------------------------------------------------------------------


class Medication(models.Model):
    """Current medications for a patient."""

    profile = models.ForeignKey(
        MedicalProfile,
        on_delete=models.CASCADE,
        related_name="medications",
    )
    name = models.CharField(max_length=150)
    dosage = models.CharField(
        max_length=80, blank=True, help_text="e.g. '500mg twice daily'"
    )
    start_date = models.DateField()
    duration_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="How many days the medication course lasts. Null = ongoing.",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "Medication"
        verbose_name_plural = "Medications"

    def __str__(self) -> str:
        return f"{self.name} ({self.dosage}) since {self.start_date}"


# ---------------------------------------------------------------------------
# MedicalEvent (accidents, fractures, bleeding, surgeries…)
# ---------------------------------------------------------------------------


class MedicalEvent(models.Model):
    """
    Historical medical events. Covers the spec fields:
    accidents, fractures, bleeding — plus general surgery / other.
    """

    profile = models.ForeignKey(
        MedicalProfile,
        on_delete=models.CASCADE,
        related_name="medical_history",
    )
    event_type = models.CharField(max_length=20, choices=MedicalEventType.choices)
    description = models.TextField()
    event_date = models.DateField()
    hospital = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ["-event_date"]
        verbose_name = "Medical Event"
        verbose_name_plural = "Medical History"

    def __str__(self) -> str:
        return f"{self.event_type} on {self.event_date} — {self.profile.user.username}"
