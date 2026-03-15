"""Django signals for the Store app - Auto-create band registrations."""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, BandRegistration


@receiver(post_save, sender=Order)
def create_band_registrations(sender, instance, created, **kwargs):
    """
    Auto-create BandRegistration when order is confirmed (paid).

    Creates one registration per band quantity purchased, linked to
    the user's medical profile.
    """
    # Only process when order status changes to processing (payment confirmed)
    if instance.status == "processing" and instance.payment_status:
        from profiles.models import MedicalProfile

        # Prefetch items to avoid N+1 query
        items = instance.items.select_related("product").all()
        for item in items:
            product = item.product

            # Check if product is a band (has the expected fields)
            if hasattr(product, "band_type"):
                for _ in range(item.quantity):
                    # Check if registration already exists for this order item
                    existing = BandRegistration.objects.filter(
                        user=instance.user, order_item=item
                    ).first()

                    if not existing:
                        # Try to get the user's medical profile
                        try:
                            medical_profile = MedicalProfile.objects.get(
                                user=instance.user
                            )
                        except MedicalProfile.DoesNotExist:
                            medical_profile = None

                        BandRegistration.objects.create(
                            user=instance.user,
                            medical_profile=medical_profile,
                            order_item=item,
                            nickname=f"Band {product.name}",
                            status="inactive",  # User must activate
                        )


@receiver(post_save, sender=Order)
def send_order_emails(sender, instance, created, **kwargs):
    """
    Send email notifications for order events.
    """
    from .emails import send_order_confirmation_email

    # Send confirmation when order is created (pending)
    if created:
        send_order_confirmation_email(instance)


@receiver(post_save, sender=Order)
def send_shipping_emails(sender, instance, created, **kwargs):
    """
    Send shipping notification when order status changes to shipped.
    """
    if not created:
        # Check if status changed to shipped
        if instance.status == "shipped" and instance.tracking_number:
            from .emails import send_shipping_notification_email

            send_shipping_notification_email(instance)


@receiver(post_save, sender=Order)
def send_delivery_emails(sender, instance, created, **kwargs):
    """
    Send delivery confirmation when order is delivered.
    """
    if not created:
        if instance.status == "delivered" and instance.delivered_at:
            from .emails import send_delivery_confirmation_email

            send_delivery_confirmation_email(instance)


@receiver(post_save, sender=BandRegistration)
def send_activation_email(sender, instance, created, **kwargs):
    """
    Send band activation instructions when a new registration is created.
    """
    if created and instance.status == "inactive":
        from .emails import send_band_activation_email

        send_band_activation_email(instance)
