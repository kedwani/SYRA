"""
Profiles/serializers.py
-----------------------
DRF serializers for the medical profile and related models.

Privacy note:
  - MedicalProfileSerializer       → general view, NO insurance data
  - InsuranceSerializer             → sensitive insurance endpoint only
  - EmergencyContactSerializer      → contacts CRUD
  - MedicationSerializer            → medications CRUD
  - MedicalEventSerializer          → history CRUD
"""

import base64
import mimetypes

from rest_framework import serializers

from .models import EmergencyContact, MedicalEvent, MedicalProfile, Medication


# ---------------------------------------------------------------------------
# EmergencyContact
# ---------------------------------------------------------------------------


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ("id", "name", "relationship", "phone_number", "priority")

    def validate(self, data: dict) -> dict:
        """Enforce max-2-contacts rule at create time."""
        profile = self.context.get("profile")
        if profile and not self.instance:
            if profile.emergency_contacts.count() >= 2:
                raise serializers.ValidationError(
                    "A patient may have at most 2 emergency contacts."
                )
        return data


# ---------------------------------------------------------------------------
# Medication
# ---------------------------------------------------------------------------


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ("id", "name", "dosage", "start_date", "duration_days", "notes")


# ---------------------------------------------------------------------------
# MedicalEvent
# ---------------------------------------------------------------------------


class MedicalEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalEvent
        fields = ("id", "event_type", "description", "event_date", "hospital")


# ---------------------------------------------------------------------------
# MedicalProfile — general (no insurance)
# ---------------------------------------------------------------------------


class MedicalProfileSerializer(serializers.ModelSerializer):
    """
    Safe for public / first-responder access.
    Intentionally excludes all insurance fields.
    """

    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    medications = MedicationSerializer(many=True, read_only=True)
    medical_history = MedicalEventSerializer(many=True, read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = MedicalProfile
        fields = (
            "id",
            "public_id",
            "username",
            "blood_type",
            "gender",
            "date_of_birth",
            "chronic_diseases",
            "immune_diseases",
            "allergies",
            "general_notes",
            "emergency_contacts",
            "medications",
            "medical_history",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "public_id", "username", "created_at", "updated_at")


# ---------------------------------------------------------------------------
# InsuranceSerializer — sensitive, served only via dedicated endpoint
# ---------------------------------------------------------------------------


class InsuranceSerializer(serializers.ModelSerializer):
    """
    Returns insurance company name plus the decrypted card image
    encoded as base64 so it can be safely embedded in a JSON response.

    The `insurance_card_image` field is write-only on input (accepts file upload)
    and appears as base64 on read (via `get_insurance_card_image`).
    """

    # Write field: accepts a raw file upload
    insurance_card_upload = serializers.ImageField(write_only=True, required=False)

    # Read field: returns base64-encoded decrypted bytes
    insurance_card_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MedicalProfile
        fields = ("insurance_company", "insurance_card_upload", "insurance_card_image")

    def get_insurance_card_image(self, obj: MedicalProfile) -> dict | None:
        """
        Decrypts the stored image and returns a dict with:
          { "content_type": "image/jpeg", "data": "<base64_string>" }
        Returns None if no image has been saved.
        """
        if not obj.insurance_card_encrypted_path:
            return None

        try:
            raw_bytes = obj.get_decrypted_insurance_image()
        except Exception:
            return None

        # Guess MIME type from stored filename extension
        mime, _ = mimetypes.guess_type(
            obj.insurance_card_encrypted_path.replace(".enc", "")
        )
        return {
            "content_type": mime or "application/octet-stream",
            "data": base64.b64encode(raw_bytes).decode("utf-8"),
        }

    def update(self, instance: MedicalProfile, validated_data: dict) -> MedicalProfile:
        upload = validated_data.pop("insurance_card_upload", None)
        instance.insurance_company = validated_data.get(
            "insurance_company", instance.insurance_company
        )
        if upload:
            instance.save_encrypted_insurance_image(upload)
        instance.save()
        return instance
