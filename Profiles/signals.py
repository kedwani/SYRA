"""Django signals for the Profiles app - Auto-create medical profiles."""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import MedicalProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_medical_profile(sender, instance, created, **kwargs):
    """
    Auto-create medical profile when user registers.
    """
    if created:
        MedicalProfile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_medical_profile(sender, instance, **kwargs):
    """
    Save profile when user is saved.
    """
    if hasattr(instance, "medical_profile"):
        instance.medical_profile.save()
