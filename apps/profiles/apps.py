"""
Django application configuration for profiles app.
"""

from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.profiles'
    verbose_name = 'Medical Profiles'
    
    def ready(self):
        try:
            import apps.profiles.signals  # noqa
        except ImportError:
            pass