from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import MedicalProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def link_or_create_profile(sender, instance, created, **kwargs):
    if created:
        # البحث عن سوار تم مسحه ولم يُربط بمستخدم بعد
        unlinked_profile = MedicalProfile.objects.filter(user__isnull=True).last()

        if unlinked_profile:
            unlinked_profile.user = instance
            unlinked_profile.save()
        else:
            # لو الحساب اتعمل من غير مسح سوار، ننشئ له بروفايل بمعرف مؤقت
            MedicalProfile.objects.create(
                user=instance, bracelet_id=f"TEMP-{instance.id}"
            )
