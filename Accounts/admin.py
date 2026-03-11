"""
Admin configuration for the Accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import SyraUser


@admin.register(SyraUser)
class SyraUserAdmin(UserAdmin):
    """Admin configuration for SyraUser."""
    
    list_display = ['username', 'email', 'national_id', 'profile_role', 'store_role', 'is_staff', 'is_active']
    list_filter = ['profile_role', 'store_role', 'is_staff', 'is_active', 'is_superuser']
    search_fields = ['username', 'email', 'national_id', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('SYRA Information', {
            'fields': ('national_id', 'phone_number', 'date_of_birth')
        }),
        ('Roles & Permissions', {
            'fields': ('profile_role', 'store_role', 'license_number', 'specialty', 'organization')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('SYRA Information', {
            'fields': ('national_id', 'phone_number', 'date_of_birth')
        }),
        ('Roles & Permissions', {
            'fields': ('profile_role', 'store_role')
        }),
    )
