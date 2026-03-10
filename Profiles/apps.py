from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Profiles"
    verbose_name = "Medical Profiles"

    def ready(self):
        # Import signals to ensure they are registered
        import Profiles.signals
    