"""
Profiles/admin.py
"""

from django.contrib import admin

from .models import EmergencyContact, MedicalEvent, MedicalProfile, Medication


class EmergencyContactInline(admin.TabularInline):
    model = EmergencyContact
    extra = 0


class MedicationInline(admin.TabularInline):
    model = Medication
    extra = 0


class MedicalEventInline(admin.TabularInline):
    model = MedicalEvent
    extra = 0


@admin.register(MedicalProfile)
class MedicalProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "blood_type", "gender", "insurance_company", "updated_at")
    search_fields = ("user__username", "user__national_id", "public_id")
    readonly_fields = (
        "public_id",
        "created_at",
        "updated_at",
        "insurance_card_encrypted_path",
    )
    inlines = [EmergencyContactInline, MedicationInline, MedicalEventInline]

    # Never expose the raw encrypted path in an editable field
    fieldsets = (
        ("Patient", {"fields": ("user", "public_id")}),
        ("Demographics", {"fields": ("blood_type", "gender", "date_of_birth")}),
        (
            "Medical",
            {
                "fields": (
                    "chronic_diseases",
                    "immune_diseases",
                    "allergies",
                    "general_notes",
                )
            },
        ),
        (
            "Insurance (sensitive)",
            {"fields": ("insurance_company", "insurance_card_encrypted_path")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
