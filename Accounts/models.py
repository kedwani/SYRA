"""
Accounts/models.py
------------------
Custom User Model for SYRA.
Extends AbstractUser to allow future auth extensions without migration pain.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class SyraUser(AbstractUser):
    """
    Custom user model for SYRA platform.
    We extend AbstractUser to keep all default Django auth fields
    (username, email, password, etc.) while leaving room for future additions.
    """

    # Use email as a required, unique identifier alongside username
    email = models.EmailField(unique=True, verbose_name="Email Address")

    # National ID for Egyptian patient identification
    national_id = models.CharField(
        max_length=14,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Egyptian National ID",
    )

    class Meta:
        verbose_name = "SYRA User"
        verbose_name_plural = "SYRA Users"

    def __str__(self) -> str:
        return f"{self.username} ({self.email})"