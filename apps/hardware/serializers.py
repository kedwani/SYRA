"""
Serializers for SYRA hardware app.
"""

from rest_framework import serializers
from apps.hardware.models import Bracelet


class BraceletSerializer(serializers.ModelSerializer):
    """
    Serializer for Bracelet model.
    """
    
    class Meta:
        model = Bracelet
        fields = [
            'id', 'serial_number', 'qr_token', 'status',
            'profile', 'ordered_at', 'shipped_at', 'delivered_at',
            'claimed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'qr_token', 'created_at', 'updated_at'
        ]


class BraceletClaimSerializer(serializers.Serializer):
    """
    Serializer for claiming a bracelet.
    """
    
    serial_number = serializers.CharField(max_length=50)
    claim_pin = serializers.CharField(max_length=6)
    profile_id = serializers.UUIDField(required=False)


class BraceletLinkSerializer(serializers.Serializer):
    """
    Serializer for linking a bracelet to a profile.
    """
    
    qr_token = serializers.UUIDField()


class BraceletStatusSerializer(serializers.Serializer):
    """
    Serializer for checking bracelet status.
    """
    
    serial_number = serializers.CharField(max_length=50)