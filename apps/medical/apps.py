"""
Django application configuration for medical app.
"""

from django.apps import AppConfig


class MedicalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.medical'
    verbose_name = 'Medical Data'
    
    def ready(self):
        try:
            import apps.medical.signals  # noqa
        except ImportError:
            pass