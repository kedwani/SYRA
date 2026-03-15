"""Django signals for the Profiles app - Auto-create medical profiles."""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.core.cache import cache
import logging

from .models import MedicalProfile, Medication, EmergencyContact, MedicalEvent

logger = logging.getLogger(__name__)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_medical_profile(sender, instance, created, **kwargs):
    """
    Auto-create medical profile when user registers.
    Uses get_or_create to handle race conditions and test scenarios.
    """
    if created:
        MedicalProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def handle_doctor_registration(sender, instance, created, **kwargs):
    """
    Handle doctor registration workflow.
    When a doctor registers, log the event for admin review.
    """
    if created and instance.profile_role == instance.ProfileRole.DOCTOR:
        logger.info(
            f"New doctor registration: {instance.username} "
            f"(License: {instance.license_number}, Specialty: {instance.specialty})"
        )
        # TODO: In production, send notification to admins
        # TODO: Consider setting is_active=False until approved


def invalidate_profile_cache(public_id):
    """Helper function to invalidate all cache variants for a profile."""
    if public_id:
        for role in ["user", "doctor", "engineer", "admin"]:
            cache_key = f"emergency_profile_{public_id}_role_{role}"
            cache.delete(cache_key)


@receiver(post_save, sender=MedicalProfile)
def invalidate_emergency_cache(sender, instance, **kwargs):
    """
    Invalidate emergency cache when profile is updated.
    This ensures emergency responders always see fresh data.
    """
    invalidate_profile_cache(instance.public_id)


@receiver(post_save, sender=Medication)
def invalidate_medication_cache(sender, instance, **kwargs):
    """Invalidate cache when medication is added/updated."""
    if instance.profile:
        invalidate_profile_cache(instance.profile.public_id)


@receiver(post_delete, sender=Medication)
def invalidate_medication_cache_delete(sender, instance, **kwargs):
    """Invalidate cache when medication is deleted."""
    if instance.profile:
        invalidate_profile_cache(instance.profile.public_id)


@receiver(post_save, sender=EmergencyContact)
def invalidate_contact_cache(sender, instance, **kwargs):
    """Invalidate cache when emergency contact is added/updated."""
    if instance.profile:
        invalidate_profile_cache(instance.profile.public_id)


@receiver(post_delete, sender=EmergencyContact)
def invalidate_contact_cache_delete(sender, instance, **kwargs):
    """Invalidate cache when emergency contact is deleted."""
    if instance.profile:
        invalidate_profile_cache(instance.profile.public_id)


@receiver(post_save, sender=MedicalEvent)
def invalidate_event_cache(sender, instance, **kwargs):
    """Invalidate cache when medical event is added/updated."""
    if instance.profile:
        invalidate_profile_cache(instance.profile.public_id)


@receiver(post_delete, sender=MedicalEvent)
def invalidate_event_cache_delete(sender, instance, **kwargs):
    """Invalidate cache when medical event is deleted."""
    if instance.profile:
        invalidate_profile_cache(instance.profile.public_id)
