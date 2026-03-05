from django.contrib import admin
from .models import MedicalProfile


@admin.register(MedicalProfile)
class MedicalProfileAdmin(admin.ModelAdmin):
    # الحقول اللي هتظهر في القائمة الرئيسية للجدول
    list_display = ["user", "blood_type", "gender", "has_insurance"]
    # حقول البحث (عشان تبحث باسم المستخدم)
    search_fields = ["user__username", "blood_type"]
    # فلاتر جانبية
    list_filter = ["blood_type", "gender", "has_insurance"]
