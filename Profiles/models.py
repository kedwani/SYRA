from django.db import models
from django.conf import settings


class MedicalProfile(models.Model):
    # ربط الملف بالمستخدم (One-to-One)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )

    # البيانات الحيوية
    blood_type = models.CharField(
        max_length=5,
        choices=[
            ("A+", "A+"),
            ("A-", "A-"),
            ("B+", "B+"),
            ("B-", "B-"),
            ("O+", "O+"),
            ("O-", "O-"),
            ("AB+", "AB+"),
            ("AB-", "AB-"),
        ],
        blank=True,
    )
    gender = models.CharField(
        max_length=10, choices=[("Male", "Male"), ("Female", "Female")], blank=True
    )
    birth_date = models.DateField(null=True, blank=True)

    # التاريخ المرضي (حوادث، كسور، نزيف قديم)
    chronic_diseases = models.TextField(blank=True)
    medical_history = models.TextField(
        blank=True, help_text="سجل الحوادث والعمليات السابقة وتواريخها"
    )

    # بيانات التأمين
    has_insurance = models.BooleanField(default=False)
    insurance_company = models.CharField(max_length=100, blank=True)
    insurance_card_photo = models.ImageField(
        upload_to="insurance_cards/", null=True, blank=True
    )

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Profile for {self.user.username}"
