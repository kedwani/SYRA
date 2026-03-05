from rest_framework import serializers
from .models import MedicalProfile


class MedicalProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = MedicalProfile
        # هنظهر كل البيانات ماعدا صورة التأمين للخصوصية في العرض العام
        exclude = ["insurance_card_photo"]


class InsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalProfile
        fields = ["insurance_card_photo"]
