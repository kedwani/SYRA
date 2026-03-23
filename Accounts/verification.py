"""Verification utilities for email and phone OTP."""

import secrets
import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


def generate_email_token():
    """Generate a secure random token for email verification."""
    return secrets.token_urlsafe(32)


def generate_phone_otp():
    """Generate a 6-digit OTP for phone verification."""
    return "".join([str(random.randint(0, 9)) for _ in range(6)])


def send_email_verification(user, request=None):
    """Send email verification link to user."""
    if not user.email:
        return False

    # Generate token if not exists
    if not user.email_verification_token:
        user.email_verification_token = generate_email_token()
        user.save()

    # Build verification URL
    from django.urls import reverse

    verify_url = (
        request.build_absolute_uri(
            reverse("verify_email", kwargs={"token": user.email_verification_token})
        )
        if request
        else f"https://syra.com/verify/email/{user.email_verification_token}"
    )

    subject = "Verify your SYRA account"
    message = f"""
    Welcome to SYRA Medical ID!
    
    Please verify your email address by clicking the link below:
    {verify_url}
    
    This link will expire in 24 hours.
    
    If you didn't create this account, please ignore this email.
    """

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def send_phone_otp(user):
    """Send OTP to user's phone number."""
    if not user.phone_number:
        return False

    # Generate OTP
    otp = generate_phone_otp()
    user.phone_otp = otp
    user.phone_otp_expiry = timezone.now() + timedelta(minutes=10)
    user.save()

    # In production, integrate with SMS provider (Twilio, etc.)
    # For now, we'll just log it
    print(f"OTP for {user.phone_number}: {otp}")

    # TODO: Integrate with SMS provider
    # Example with Twilio:
    # from twilio.rest import Client
    # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    # client.messages.create(
    #     body=f"Your SYRA verification code is: {otp}",
    #     from_=settings.TWILIO_PHONE_NUMBER,
    #     to=user.phone_number
    # )

    return True


def verify_phone_otp(user, otp):
    """Verify the OTP entered by user."""
    if not user.phone_otp or not user.phone_otp_expiry:
        return False

    # Check if OTP is expired
    if timezone.now() > user.phone_otp_expiry:
        user.phone_otp = ""
        user.phone_otp_expiry = None
        user.save()
        return False

    # Check if OTP matches
    if user.phone_otp == otp:
        user.is_phone_verified = True
        user.phone_otp = ""
        user.phone_otp_expiry = None
        user.save()
        return True

    return False
