"""Models for the Accounts app."""

import re
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


def validate_egyptian_national_id(value):
    """Validate Egyptian National ID - must be exactly 14 digits."""
    if not re.match(r"^\d{14}$", str(value)):
        raise ValidationError(
            "Egyptian National ID must be exactly 14 digits.",
            code="invalid_national_id",
        )


class SyraUser(AbstractUser):
    """
    Extended User model for SYRA.
    Includes 14-digit Egyptian National ID as primary identifier.
    """

    class ProfileRole(models.TextChoices):
        USER = "user", "Regular User"
        DOCTOR = "doctor", "Doctor"
        ENGINEER = "engineer", "Engineer/Worker"
        ADMIN = "admin", "Administrator"

    class StoreRole(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        PRODUCT_MANAGER = "product_manager", "Product Manager"
        PRICE_MANAGER = "price_manager", "Price Manager"
        STORE_VIEWER = "store_viewer", "Store Viewer/Analyst"
        STORE_ADMIN = "store_admin", "Store Administrator"

    national_id = models.CharField(
        max_length=14,
        unique=True,
        validators=[validate_egyptian_national_id],
        verbose_name="Egyptian National ID",
        help_text="14-digit Egyptian National ID",
    )
    phone_number = models.CharField(
        max_length=11, blank=True, verbose_name="Phone Number"
    )
    date_of_birth = models.DateField(
        null=True, blank=True, verbose_name="Date of Birth"
    )

    # Role fields
    profile_role = models.CharField(
        max_length=20,
        choices=ProfileRole.choices,
        default=ProfileRole.USER,
        verbose_name="Profile Access Role",
    )
    store_role = models.CharField(
        max_length=20,
        choices=StoreRole.choices,
        default=StoreRole.CUSTOMER,
        verbose_name="Store Portal Role",
    )

    # Additional fields
    license_number = models.CharField(
        max_length=50, blank=True, verbose_name="Professional License Number"
    )
    specialty = models.CharField(
        max_length=100, blank=True, verbose_name="Medical Specialty (for doctors)"
    )
    organization = models.CharField(
        max_length=200, blank=True, verbose_name="Organization/Company"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SYRA User"
        verbose_name_plural = "SYRA Users"

    def __str__(self):
        return f"{self.username} ({self.national_id})"

    @property
    def is_doctor(self):
        """Check if user is a doctor."""
        return self.profile_role == self.ProfileRole.DOCTOR

    @property
    def is_engineer(self):
        """Check if user is an engineer/worker."""
        return self.profile_role == self.ProfileRole.ENGINEER

    @property
    def is_profile_admin(self):
        """Check if user has admin access to profiles."""
        return self.profile_role == self.ProfileRole.ADMIN

    @property
    def can_view_full_profile(self):
        """Check if user can view full medical profile."""
        return self.profile_role in [self.ProfileRole.DOCTOR, self.ProfileRole.ADMIN]

    @property
    def can_manage_products(self):
        """Check if user can add/manage products."""
        return self.store_role in [
            self.StoreRole.PRODUCT_MANAGER,
            self.StoreRole.STORE_ADMIN,
        ]

    @property
    def can_manage_prices(self):
        """Check if user can manage prices."""
        return self.store_role in [
            self.StoreRole.PRICE_MANAGER,
            self.StoreRole.STORE_ADMIN,
        ]

    @property
    def can_view_store_analytics(self):
        """Check if user can view store analytics."""
        return self.store_role in [
            self.StoreRole.STORE_VIEWER,
            self.StoreRole.STORE_ADMIN,
            self.StoreRole.PRICE_MANAGER,
        ]

    @property
    def can_manage_orders(self):
        """Check if user can manage orders."""
        return self.store_role in [
            self.StoreRole.STORE_ADMIN,
            self.StoreRole.STORE_VIEWER,
        ]
