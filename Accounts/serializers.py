"""Serializers for the Accounts API."""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import SyraUser

User = get_user_model()


class SyraUserSerializer(serializers.ModelSerializer):
    """Serializer for SyraUser model."""
    
    class Meta:
        model = SyraUser
        fields = ['id', 'username', 'email', 'phone_number', 'date_of_birth', 'first_name', 'last_name']
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = SyraUser
        fields = ['username', 'email', 'password', 'password_confirm', 'national_id', 'phone_number', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        
        # Check if National ID already exists
        if SyraUser.objects.filter(national_id=attrs['national_id']).exists():
            raise serializers.ValidationError({'national_id': 'This National ID is already registered.'})
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = SyraUser.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    national_id = serializers.CharField()
    password = serializers.CharField(write_only=True)
