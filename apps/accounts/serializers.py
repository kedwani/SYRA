"""
Serializers for SYRA accounts app.
Handles user registration, login, and profile serialization.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from apps.accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'phone', 'date_of_birth', 'blood_type',
            'avatar', 'is_medical_personnel', 'medical_license_number',
            'hospital_name', 'hospital_verified', 'subscription_type',
            'agreed_to_terms', 'privacy_consent', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_medical_personnel', 'hospital_verified',
            'subscription_type', 'created_at', 'updated_at'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    agreed_to_terms = serializers.BooleanField(write_only=True)
    privacy_consent = serializers.BooleanField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'date_of_birth',
            'blood_type', 'agreed_to_terms', 'privacy_consent'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match'
            })
        
        if not attrs.get('agreed_to_terms'):
            raise serializers.ValidationError({
                'agreed_to_terms': 'You must agree to the terms of service'
            })
        
        if not attrs.get('privacy_consent'):
            raise serializers.ValidationError({
                'privacy_consent': 'You must consent to privacy policy'
            })
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        validated_data.pop('agreed_to_terms', None)
        validated_data.pop('privacy_consent', None)
        
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username', validated_data['email'].split('@')[0]),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            date_of_birth=validated_data.get('date_of_birth'),
            blood_type=validated_data.get('blood_type', 'UNKNOWN'),
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Invalid email or password')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Email and password are required')
        
        return attrs


class TokenResponseSerializer(serializers.Serializer):
    """
    Serializer for JWT token response.
    """
    
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password.
    """
    
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match'
            })
        return attrs
    
    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect')
        return value


class MedicalPersonnelSerializer(serializers.ModelSerializer):
    """
    Serializer for medical personnel verification.
    """
    
    class Meta:
        model = User
        fields = [
            'is_medical_personnel', 'medical_license_number',
            'hospital_name', 'hospital_verified'
        ]
        read_only_fields = ['hospital_verified']
    
    def update(self, instance, validated_data):
        instance.is_medical_personnel = True
        instance.medical_license_number = validated_data.get(
            'medical_license_number', instance.medical_license_number
        )
        instance.hospital_name = validated_data.get(
            'hospital_name', instance.hospital_name
        )
        instance.save()
        return instance