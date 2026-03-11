"""Profiles app configuration."""

from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "profiles"
    verbose_name = "Medical Profiles"

    def ready(self):
        import profiles.signals  # Import signals on app load
