"""
Serializers for SYRA profiles app.
"""

from rest_framework import serializers
from apps.accounts.serializers import UserSerializer
from apps.profiles.models import MedicalProfile


class MedicalProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for MedicalProfile model.
    """
    
    user = UserSerializer(read_only=True)
    qr_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicalProfile
        fields = [
            'id', 'user', 'qr_token', 'qr_token_hash', 'qr_url',
            'default_visibility', 'is_active', 'emergency_note',
            'created_at', 'updated_at', 'last_accessed_at'
        ]
        read_only_fields = [
            'id', 'qr_token', 'qr_token_hash', 'created_at',
            'updated_at', 'last_accessed_at'
        ]
    
    def get_qr_url(self, obj):
        request = self.context.get('request')
        if request:
            base_url = request.build_absolute_uri('/').rstrip('/')
            return f"{base_url}/e/{obj.qr_token_hash}"
        return f"/e/{obj.qr_token_hash}"


class MedicalProfileCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating MedicalProfile.
    """
    
    class Meta:
        model = MedicalProfile
        fields = ['default_visibility', 'emergency_note']
    
    def create(self, validated_data):
        user = self.context['request'].user
        return MedicalProfile.objects.create(
            user=user,
            qr_token=validated_data.get('qr_token'),
            default_visibility=validated_data.get('default_visibility', 'public'),
            emergency_note=validated_data.get('emergency_note', '')
        )


class ProfileVisibilitySerializer(serializers.Serializer):
    """
    Serializer for updating visibility settings.
    """
    
    default_visibility = serializers.ChoiceField(
        choices=MedicalProfile.VISIBILITY_CHOICES
    )


class QRCodeSerializer(serializers.Serializer):
    """
    Serializer for QR code response.
    """
    
    qr_token_hash = serializers.CharField()
    qr_url = serializers.CharField()
    qr_image = serializers.CharField(allow_null=True)