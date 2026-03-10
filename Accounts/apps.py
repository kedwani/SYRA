"""
Accounts/apps.py
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Accounts"

    def ready(self) -> None:
        # Import signals so they are registered on app startup
        import Profiles.signals  # noqa: F401
