from rest_framework import serializers
from .models import MedicalProfile, EmergencyContact


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ["name", "relationship", "phone_number"]


class MedicalProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")
    contacts = EmergencyContactSerializer(many=True, read_only=True)

    class Meta:
        model = MedicalProfile
        exclude = ["insurance_card_photo"]


class InsuranceCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalProfile
        fields = ["insurance_card_photo"]
