from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Profiles"

    def ready(self):
        # الـ import لازم يكون جوه الدالة دي مش فوق
        import Profiles.signals
