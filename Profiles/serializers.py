from rest_framework import serializers
from .models import MedicalProfile


class MedicalProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = MedicalProfile
        # إخفاء صورة التأمين من العرض العام لزيادة الأمان والخصوصية
        exclude = ["insurance_card_photo"]


class InsuranceCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalProfile
        fields = ["insurance_card_photo"]
