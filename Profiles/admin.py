from django.contrib import admin
from .models import MedicalProfile, EmergencyContact, ScanRecord


@admin.register(ScanRecord)
class ScanRecordAdmin(admin.ModelAdmin):
    list_display = ("profile", "scan_time", "ip_address")
    list_filter = ("scan_time",)


admin.site.register(MedicalProfile)
admin.site.register(EmergencyContact)
