"""
Profiles/signals.py
-------------------
Django signal: automatically create a blank MedicalProfile whenever
a new SyraUser is saved for the first time.

This satisfies the Phase 1 requirement: "Use signals to automatically
create a MedicalProfile whenever a new user is registered."
"""

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MedicalProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_medical_profile(sender, instance, created: bool, **kwargs) -> None:
    """
    Fires after every SyraUser save.
    Only acts on the very first save (created=True) to avoid
    overwriting data on subsequent profile updates.
    """
    if created:
        MedicalProfile.objects.create(user=instance)
