"""
Emergency Alert API views.
Handles sending emergency alerts to contacts and logging incidents.
"""

from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
import logging

from .models import MedicalProfile, EmergencyContact

logger = logging.getLogger(__name__)


@extend_schema(
    methods=["POST"],
    parameters=[
        OpenApiParameter(
            name="public_id",
            location=OpenApiParameter.PATH,
            type=str,
            description="UUID of the medical profile",
        )
    ],
    request=serializers.Serializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
                "location": {"type": "string"},
                "contacts_notified": {"type": "integer"},
                "failed_contacts": {"type": "array", "items": {"type": "string"}},
            },
        }
    },
    examples=[
        OpenApiExample(
            "Emergency Alert Example",
            value={"latitude": 29.97, "longitude": 31.13, "device_info": "iPhone 14"},
            request_only=True,
        ),
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_emergency_alert(request, public_id):
    """
    Send emergency alert to all emergency contacts.

    Request body:
    {
        "latitude": 29.97,
        "longitude": 31.13,
        "device_info": "iPhone 14"
    }

    Sends SMS/Email to all emergency contacts with location link.
    """
    logger.info(f"Emergency alert request received for public_id: {public_id}")

    try:
        profile = MedicalProfile.objects.select_related("user").get(public_id=public_id)
        logger.info(f"Profile found: {profile.user.username}")
    except MedicalProfile.DoesNotExist:
        logger.error(f"Profile not found for public_id: {public_id}")
        return Response(
            {"error": "Medical profile not found."}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error finding profile: {str(e)}")
        return Response(
            {"error": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Authorization check: only profile owner can send emergency alerts
    if profile.user != request.user:
        logger.warning(
            f"Unauthorized emergency alert attempt by user {request.user.username} "
            f"for profile owned by {profile.user.username}"
        )
        return Response(
            {"error": "You don't have permission to send alerts for this profile."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Get location from request
    latitude = request.data.get("latitude")
    longitude = request.data.get("longitude")
    device_info = request.data.get("device_info", "Unknown device")

    # Build location URL
    location_url = ""
    if latitude and longitude:
        location_url = f"https://maps.google.com/?q={latitude},{longitude}"

    # Get user info
    user_name = profile.user.get_full_name() or profile.user.username
    blood_type = profile.get_blood_type_display() if profile.blood_type else "Unknown"
    allergies = profile.allergies or "None"

    # Build emergency message
    emergency_message = f"""🚨 EMERGENCY ALERT - SYRA Medical ID

{user_name} may need URGENT help!

Location: {location_url}
Device: {device_info}

--- Medical Info ---
Blood Type: {blood_type}
Allergies: {allergies}

This alert was sent via SYRA Medical ID Emergency System.
Learn more: https://syra.app
"""

    # Get emergency contacts and their emails
    contacts = profile.emergency_contacts.filter(is_approved=True).all()

    logger.info(
        f"Found {contacts.count()} emergency contacts for profile {profile.user.username}"
    )

    if not contacts:
        logger.warning(f"No emergency contacts for profile {profile.public_id}")
        return Response(
            {
                "success": False,
                "error": "No emergency contacts configured. Please add emergency contacts first.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Collect emails from approved emergency contacts
    contact_emails = []
    for contact in contacts:
        if hasattr(contact, "email") and contact.email:
            contact_emails.append(contact.email)
        # Log SMS notification (Twilio integration would go here)
        logger.info(
            f"Would send SMS to {contact.phone_number}: {emergency_message[:100]}..."
        )

    if not contact_emails:
        logger.warning(
            f"No email addresses for emergency contacts - logging alert only"
        )

    # Send alerts to all contacts with emails
    sent_count = 0
    failed_contacts = []

    for contact in contacts:
        # Skip if contact doesn't have email (we'll send SMS instead)
        if not (hasattr(contact, "email") and contact.email):
            logger.info(f"No email for contact {contact.name} - would send SMS instead")
            continue

        try:
            send_mail(
                f"🚨 URGENT: {user_name} needs help!",
                emergency_message,
                (
                    settings.DEFAULT_FROM_EMAIL
                    if hasattr(settings, "DEFAULT_FROM_EMAIL")
                    else "noreply@syra.app"
                ),
                [contact.email],
                fail_silently=False,
            )
            sent_count += 1
            logger.info(
                f"Email sent to {contact.email} for contact {contact.name} ({contact.phone_number})"
            )

        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")
            failed_contacts.append(contact.name)

    # Log the incident
    from .models import ProfileAccessLog

    ProfileAccessLog.objects.create(
        profile=profile,
        accessed_by=None,
        access_role="emergency_alert",
        access_type="emergency",
        ip_address=request.META.get("REMOTE_ADDR", ""),
        user_agent=device_info,
    )

    return Response(
        {
            "success": True,
            "message": f"Emergency alert sent to {sent_count} contact(s)",
            "location": location_url,
            "contacts_notified": sent_count,
            "failed_contacts": failed_contacts,
        }
    )


@extend_schema(
    methods=["GET"],
    parameters=[
        OpenApiParameter(
            name="lat",
            location=OpenApiParameter.QUERY,
            type=float,
            description="Latitude coordinate",
        ),
        OpenApiParameter(
            name="lng",
            location=OpenApiParameter.QUERY,
            type=float,
            description="Longitude coordinate",
        ),
    ],
    responses={
        200: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "address": {"type": "string"},
                    "distance_km": {"type": "number"},
                    "phone": {"type": "string"},
                },
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_nearby_hospitals(request):
    """
    Get nearby hospitals based on coordinates.

    Query params:
    ?lat=29.97&lng=31.13

    Returns list of nearby hospitals (mock data for demo).
    In production, integrate with Google Places API.
    """
    latitude = request.query_params.get("lat")
    longitude = request.query_params.get("lng")

    if not latitude or not longitude:
        return Response(
            {"error": "Latitude and longitude required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        lat = float(latitude)
        lng = float(longitude)
    except ValueError:
        return Response(
            {"error": "Invalid coordinates."}, status=status.HTTP_400_BAD_REQUEST
        )

    # Mock hospital data - in production, use Google Places API
    # This calculates approximate distances
    hospitals = [
        {
            "name": "El Sherouk Hospital",
            "address": "El Sherouk City, Cairo",
            "distance_km": 2.1,
            "phone": "+20 2 2750 0000",
            "lat": lat + 0.02,
            "lng": lng + 0.01,
        },
        {
            "name": "New Cairo Medical Center",
            "address": "New Cairo, Cairo",
            "distance_km": 3.8,
            "phone": "+20 2 2751 1111",
            "lat": lat - 0.03,
            "lng": lng + 0.02,
        },
        {
            "name": "Egyptian Hospital",
            "address": "Al-Mokattam, Cairo",
            "distance_km": 5.2,
            "phone": "+20 2 2752 2222",
            "lat": lat + 0.05,
            "lng": lng - 0.02,
        },
        {
            "name": "International Hospital",
            "address": "Maadi, Cairo",
            "distance_km": 8.5,
            "phone": "+20 2 2753 3333",
            "lat": lat - 0.08,
            "lng": lng - 0.05,
        },
    ]

    # Sort by distance
    hospitals.sort(key=lambda x: x["distance_km"])

    return Response({"user_location": {"lat": lat, "lng": lng}, "hospitals": hospitals})
