from django.db import models
from django.conf import settings


class MedicalProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        null=True,
        blank=True,
    )
    bracelet_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
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
    chronic_diseases = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)
    has_insurance = models.BooleanField(default=False)
    insurance_company = models.CharField(max_length=100, blank=True)
    insurance_card_photo = models.ImageField(
        upload_to="insurance_cards/", null=True, blank=True
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Profile: {self.bracelet_id}"


class EmergencyContact(models.Model):
    profile = models.ForeignKey(
        MedicalProfile, on_delete=models.CASCADE, related_name="contacts"
    )
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)


# الموديل الجديد لتتبع المسح
class ScanRecord(models.Model):
    profile = models.ForeignKey(
        MedicalProfile, on_delete=models.CASCADE, related_name="scans"
    )
    scan_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)  # نوع الجهاز اللي مسح الكود

    def __str__(self):
        return f"Scan for {self.profile.bracelet_id} at {self.scan_time}"
