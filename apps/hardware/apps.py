"""
Django application configuration for hardware app.
"""

from django.apps import AppConfig


class HardwareConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.hardware'
    verbose_name = 'Hardware Management'
    
    def ready(self):
        try:
            import apps.hardware.signals  # noqa
        except ImportError:
            pass