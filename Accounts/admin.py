"""
Accounts/admin.py
-----------------
Register SyraUser with the Django admin site.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import SyraUser


@admin.register(SyraUser)
class SyraUserAdmin(UserAdmin):
    """Extend the default UserAdmin to show our custom fields."""

    list_display = ("username", "email", "national_id", "is_staff", "date_joined")
    fieldsets = UserAdmin.fieldsets + (("SYRA Info", {"fields": ("national_id",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("SYRA Info", {"fields": ("email", "national_id")}),
    )

    search_fields = ("username", "email", "national_id")
    ordering = ("date_joined",)
