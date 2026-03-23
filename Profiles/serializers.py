"""Serializers for the Profiles API."""

from rest_framework import serializers
from .models import MedicalProfile, Medication, EmergencyContact, MedicalEvent


class MedicationSerializer(serializers.ModelSerializer):
    """Serializer for Medication model."""

    class Meta:
        model = Medication
        fields = [
            "id",
            "name",
            "dosage",
            "frequency",
            "period_days",
            "is_active",
            "notes",
            "added_by_doctor",
            "pending_approval",
            "is_approved",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EmergencyContactSerializer(serializers.ModelSerializer):
    """Serializer for EmergencyContact model."""

    class Meta:
        model = EmergencyContact
        fields = [
            "id",
            "name",
            "relationship",
            "phone_number",
            "alternate_phone",
            "is_primary",
            "added_by_doctor",
            "pending_approval",
            "is_approved",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        # Enforce max 2 emergency contacts
        profile = validated_data["profile"]
        if profile.emergency_contacts.count() >= 2:
            raise serializers.ValidationError(
                "Maximum of 2 emergency contacts allowed."
            )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Check if adding would exceed limit
        if "profile" not in validated_data:
            return super().update(instance, validated_data)

        profile = validated_data["profile"]
        if profile.emergency_contacts.count() >= 2 and instance.profile != profile:
            raise serializers.ValidationError(
                "Maximum of 2 emergency contacts allowed."
            )
        return super().update(instance, validated_data)


class MedicalEventSerializer(serializers.ModelSerializer):
    """Serializer for MedicalEvent model."""

    class Meta:
        model = MedicalEvent
        fields = [
            "id",
            "event_type",
            "title",
            "description",
            "date",
            "hospital_name",
            "doctor_name",
            "added_by_doctor",
            "pending_approval",
            "is_approved",
            "approved_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MedicalProfileSerializer(serializers.ModelSerializer):
    """Serializer for MedicalProfile model - includes nested relationships."""

    medications = MedicationSerializer(many=True, read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    medical_events = MedicalEventSerializer(many=True, read_only=True)

    class Meta:
        model = MedicalProfile
        fields = [
            "id",
            "public_id",
            "blood_type",
            "chronic_diseases",
            "allergies",
            "emergency_notes",
            "insurance_provider",
            "insurance_number",
            "insurance_image",
            "height",
            "weight",
            "medications",
            "emergency_contacts",
            "medical_events",
            # Visibility controls
            "show_blood_type_public",
            "show_allergies_public",
            "show_medications_public",
            "show_contacts_public",
            "show_physical_public",
            "show_history_public",
            "show_chronic_diseases_public",
            "show_notes_public",
            "show_insurance_public",
            "premium_access_logging",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "public_id", "created_at", "updated_at"]


class EmergencyProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for emergency view - excludes sensitive insurance data.
    Only exposes life-saving information for first responders.
    Respects visibility control flags from the profile.
    """

    medications = MedicationSerializer(many=True, read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)

    class Meta:
        model = MedicalProfile
        fields = [
            "public_id",
            "blood_type",
            "chronic_diseases",
            "allergies",
            "emergency_notes",
            "height",
            "weight",
            "medications",
            "emergency_contacts",
            # Visibility controls
            "show_blood_type_public",
            "show_allergies_public",
            "show_medications_public",
            "show_contacts_public",
            "show_physical_public",
            "show_history_public",
            "show_chronic_diseases_public",
            "show_notes_public",
        ]

    def to_representation(self, instance):
        """Filter fields based on visibility settings."""
        data = super().to_representation(instance)

        # Filter based on visibility controls - hide actual values but keep flags
        # Blood type
        if not getattr(instance, "show_blood_type_public", True):
            data["blood_type"] = None

        # Allergies
        if not getattr(instance, "show_allergies_public", True):
            data["allergies"] = None

        # Medications
        if not getattr(instance, "show_medications_public", True):
            data["medications"] = []

        # Emergency contacts
        if not getattr(instance, "show_contacts_public", True):
            data["emergency_contacts"] = []

        # Physical info (height/weight)
        if not getattr(instance, "show_physical_public", False):
            data["height"] = None
            data["weight"] = None

        # Chronic diseases (part of medical history)
        if not getattr(instance, "show_history_public", False):
            data["chronic_diseases"] = None

        return data
