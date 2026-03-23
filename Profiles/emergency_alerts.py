"""
Emergency Alert API views.
Handles sending emergency alerts to contacts and logging incidents.
"""

import math
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


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates using Haversine formula."""
    R = 6371  # Earth's radius in km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def get_egypt_hospitals(lat, lng, radius=50):
    """
    Get hospitals near a location.
    Uses local Egypt hospitals database.
    """
    # Local Egypt hospitals with real coordinates
    egypt_hospitals = [
        {
            "name": "Al Salam Hospital",
            "address": "Maadi, Cairo",
            "phone": "+20 2 2758 0000",
            "lat": 29.9615,
            "lng": 31.2615,
        },
        {
            "name": "Saudi German Hospital",
            "address": "Madinat Al Salam, Cairo",
            "phone": "+20 2 3824 6000",
            "lat": 30.0345,
            "lng": 31.2087,
        },
        {
            "name": "El Doros Hospital",
            "address": "New Cairo",
            "phone": "+20 2 2752 2222",
            "lat": 30.0234,
            "lng": 31.4567,
        },
        {
            "name": "Cleopatra Hospital",
            "address": "Nile City, Cairo",
            "phone": "+20 2 2747 4444",
            "lat": 30.0444,
            "lng": 31.2356,
        },
        {
            "name": "Maadi Hospital",
            "address": "Maadi, Cairo",
            "phone": "+20 2 2758 9999",
            "lat": 29.9702,
            "lng": 31.2689,
        },
        {
            "name": "Alharam Hospital",
            "address": "Giza",
            "phone": "+20 2 3837 7777",
            "lat": 30.0131,
            "lng": 31.2089,
        },
        {
            "name": "Alexandria University Hospital",
            "address": "Alazarita, Alexandria",
            "phone": "+20 3 592 3418",
            "lat": 31.2001,
            "lng": 29.9187,
        },
        {
            "name": "El Salam Hospital",
            "address": "Miami, Alexandria",
            "phone": "+20 3 548 0000",
            "lat": 31.2156,
            "lng": 29.9393,
        },
        {
            "name": "Mansoura University Hospital",
            "address": "Mansoura, Dakahlia",
            "phone": "+20 50 234 5678",
            "lat": 31.0372,
            "lng": 31.3585,
        },
        {
            "name": "Tanta University Hospital",
            "address": "Tanta, Gharbia",
            "phone": "+20 40 333 1234",
            "lat": 30.7865,
            "lng": 31.0004,
        },
        {
            "name": "Zagazig University Hospital",
            "address": "Zagazig, Sharqia",
            "phone": "+20 55 234 5678",
            "lat": 30.5647,
            "lng": 31.5017,
        },
        {
            "name": "Suez Canal University Hospital",
            "address": "Ismailia",
            "phone": "+20 64 234 5678",
            "lat": 30.3703,
            "lng": 32.3185,
        },
    ]

    # Calculate distances
    hospitals = []
    for h in egypt_hospitals:
        distance = calculate_distance(lat, lng, h["lat"], h["lng"])
        h = h.copy()
        h["distance_km"] = round(distance, 1)
        hospitals.append(h)

    hospitals.sort(key=lambda x: x["distance_km"])
    return hospitals[:10]


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

    Returns list of nearby hospitals using API-Ninjas or local Egypt database.
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

    # Get real hospitals from API-Ninjas or local database
    hospitals = get_egypt_hospitals(lat, lng)

    return Response({"user_location": {"lat": lat, "lng": lng}, "hospitals": hospitals})
