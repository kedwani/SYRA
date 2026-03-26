"""
Serializers for SYRA medical app.
"""

from rest_framework import serializers
from apps.medical.models import Allergy, Medication, Condition, EmergencyContact
from apps.profiles.models import MedicalProfile


class AllergySerializer(serializers.ModelSerializer):
    """
    Serializer for Allergy model.
    """
    
    class Meta:
        model = Allergy
        fields = [
            'id', 'name', 'severity', 'visibility', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        profile = self.context['profile']
        return Allergy.objects.create(profile=profile, **validated_data)


class MedicationSerializer(serializers.ModelSerializer):
    """
    Serializer for Medication model.
    """
    
    class Meta:
        model = Medication
        fields = [
            'id', 'name', 'dosage', 'frequency', 'visibility',
            'prescribed_by', 'reason', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        profile = self.context['profile']
        return Medication.objects.create(profile=profile, **validated_data)


class ConditionSerializer(serializers.ModelSerializer):
    """
    Serializer for Condition model.
    """
    
    class Meta:
        model = Condition
        fields = [
            'id', 'name', 'severity', 'visibility', 'diagnosed_date',
            'notes', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        profile = self.context['profile']
        return Condition.objects.create(profile=profile, **validated_data)


class EmergencyContactSerializer(serializers.ModelSerializer):
    """
    Serializer for EmergencyContact model.
    """
    
    class Meta:
        model = EmergencyContact
        fields = [
            'id', 'name', 'relationship', 'phone', 'email',
            'is_primary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        profile = self.context['profile']
        
        # If this is marked as primary, unset other primary contacts
        if validated_data.get('is_primary'):
            EmergencyContact.objects.filter(
                profile=profile, is_primary=True
            ).update(is_primary=False)
        
        return EmergencyContact.objects.create(profile=profile, **validated_data)
    
    def update(self, instance, validated_data):
        # If this is marked as primary, unset other primary contacts
        if validated_data.get('is_primary'):
            EmergencyContact.objects.filter(
                profile=instance.profile, is_primary=True
            ).exclude(pk=instance.pk).update(is_primary=False)
        
        return super().update(instance, validated_data)


class MedicalDataSerializer(serializers.Serializer):
    """
    Comprehensive serializer for all medical data.
    """
    
    allergies = AllergySerializer(many=True, read_only=True)
    medications = MedicationSerializer(many=True, read_only=True)
    conditions = ConditionSerializer(many=True, read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)