"""Serializers for the Profiles API."""
from rest_framework import serializers
from .models import MedicalProfile, Medication, EmergencyContact, MedicalEvent


class MedicationSerializer(serializers.ModelSerializer):
    """Serializer for Medication model."""
    
    class Meta:
        model = Medication
        fields = ['id', 'name', 'dosage', 'frequency', 'is_active', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmergencyContactSerializer(serializers.ModelSerializer):
    """Serializer for EmergencyContact model."""
    
    class Meta:
        model = EmergencyContact
        fields = ['id', 'name', 'relationship', 'phone_number', 'alternate_phone', 'is_primary', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Enforce max 2 emergency contacts
        profile = validated_data['profile']
        if profile.emergency_contacts.count() >= 2:
            raise serializers.ValidationError(
                'Maximum of 2 emergency contacts allowed.'
            )
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Check if adding would exceed limit
        if 'profile' not in validated_data:
            return super().update(instance, validated_data)
        
        profile = validated_data['profile']
        if profile.emergency_contacts.count() >= 2 and instance.profile != profile:
            raise serializers.ValidationError(
                'Maximum of 2 emergency contacts allowed.'
            )
        return super().update(instance, validated_data)


class MedicalEventSerializer(serializers.ModelSerializer):
    """Serializer for MedicalEvent model."""
    
    class Meta:
        model = MedicalEvent
        fields = ['id', 'event_type', 'title', 'description', 'date', 'hospital_name', 'doctor_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class MedicalProfileSerializer(serializers.ModelSerializer):
    """Serializer for MedicalProfile model - includes nested relationships."""
    medications = MedicationSerializer(many=True, read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    medical_events = MedicalEventSerializer(many=True, read_only=True)
    
    class Meta:
        model = MedicalProfile
        fields = [
            'id', 'public_id', 'blood_type', 'chronic_diseases', 'allergies',
            'emergency_notes', 'insurance_provider', 'insurance_number',
            'insurance_image', 'height', 'weight', 'medications',
            'emergency_contacts', 'medical_events', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'public_id', 'created_at', 'updated_at']


class EmergencyProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for emergency view - excludes sensitive insurance data.
    Only exposes life-saving information for first responders.
    """
    medications = MedicationSerializer(many=True, read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    
    class Meta:
        model = MedicalProfile
        fields = [
            'public_id', 'blood_type', 'chronic_diseases', 'allergies',
            'emergency_notes', 'height', 'weight', 'medications', 'emergency_contacts'
        ]
