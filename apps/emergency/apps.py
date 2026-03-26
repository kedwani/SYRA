"""
Django application configuration for emergency app.
"""

from django.apps import AppConfig


class EmergencyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.emergency'
    verbose_name = 'Emergency Access'
    
    def ready(self):
        try:
            import apps.emergency.signals  # noqa
        except ImportError:
            pass