from django.contrib import admin
from .models import MedicalProfile, EmergencyContact


class EmergencyContactInline(admin.TabularInline):
    model = EmergencyContact
    extra = 1


@admin.register(MedicalProfile)
class MedicalProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "blood_type", "gender", "has_insurance"]
    search_fields = ["user__username"]
    inlines = [EmergencyContactInline]
