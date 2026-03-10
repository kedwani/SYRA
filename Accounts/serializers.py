"""
Accounts/serializers.py
-----------------------
Serializers for user registration and authentication.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Handles new user creation. Password is write-only and confirmed
    before saving. Signal will auto-create MedicalProfile on save.
    """

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "national_id",
            "password",
            "password_confirm",
        )

    def validate(self, data: dict) -> dict:
        if data["password"] != data.pop("password_confirm"):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """Read-only public user info. Never exposes password."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "national_id", "date_joined")
        read_only_fields = fields
