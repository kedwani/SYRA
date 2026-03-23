"""Views for the Profiles app."""

from rest_framework import viewsets, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from .models import MedicalProfile, Medication, EmergencyContact, MedicalEvent
from .serializers import (
    MedicalProfileSerializer,
    EmergencyProfileSerializer,
    MedicationSerializer,
    EmergencyContactSerializer,
    MedicalEventSerializer,
)
from .medical_data import search_medications, search_diagnoses
from .emergency_alerts import send_emergency_alert, get_nearby_hospitals
from django.http import FileResponse, Http404
import logging

logger = logging.getLogger(__name__)


def get_user_role(user):
    """
    Get user profile role for access control.
    Returns 'user' for anonymous/unauthenticated users.
    """
    if not user or not user.is_authenticated:
        return "user"
    return getattr(user, "profile_role", "user")


class MedicalProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for MedicalProfile - CRUD operations."""

    queryset = MedicalProfile.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "public_id"

    def get_serializer_class(self):
        if self.action == "retrieve":
            # Check if this is the emergency view (by UUID without auth)
            if hasattr(self, "kwargs") and "pk" in self.kwargs:
                try:
                    profile = MedicalProfile.objects.get(public_id=self.kwargs["pk"])
                    return EmergencyProfileSerializer
                except MedicalProfile.DoesNotExist:
                    pass
        return MedicalProfileSerializer

    def get_queryset(self):
        # Non-admin users can only see their own profile
        user = self.request.user
        if user.is_staff or getattr(user, "profile_role", "") == "admin":
            return MedicalProfile.objects.all()
        return MedicalProfile.objects.filter(user=user)

    def get_object(self):
        """Get object with ownership check."""
        # Use public_id for lookup
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        # Get the filter kwargs
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        # Get queryset with ownership filter
        queryset = self.get_queryset()

        try:
            obj = queryset.get(**filter_kwargs)
        except MedicalProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound("Medical profile not found.")

        # Check if user owns this profile (additional security)
        if obj.user != self.request.user and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You can only access your own medical profile.")

        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Disable list action for individual profiles (users only see their own)
    def list(self, request, *args, **kwargs):
        from rest_framework.exceptions import MethodNotAllowed

        raise MethodNotAllowed("GET", detail="Listing all profiles is not allowed.")


class MedicationViewSet(viewsets.ModelViewSet):
    """ViewSet for Medication - CRUD operations."""

    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Medication.objects.filter(profile__user=self.request.user)

    def perform_create(self, serializer):
        try:
            profile = self.request.user.medical_profile
        except MedicalProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound("Please create a medical profile first.")
        serializer.save(profile=profile)


class EmergencyContactViewSet(viewsets.ModelViewSet):
    """ViewSet for EmergencyContact - CRUD operations."""

    queryset = EmergencyContact.objects.all()
    serializer_class = EmergencyContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EmergencyContact.objects.filter(profile__user=self.request.user)

    def perform_create(self, serializer):
        try:
            profile = self.request.user.medical_profile
        except MedicalProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound("Please create a medical profile first.")

        # Enforce max 2 emergency contacts
        if profile.emergency_contacts.count() >= 2:
            from rest_framework.exceptions import ValidationError

            raise ValidationError(
                {"detail": "Maximum of 2 emergency contacts allowed."}
            )

        serializer.save(profile=profile)

    def perform_update(self, serializer):
        try:
            profile = self.request.user.medical_profile
        except MedicalProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound("Please create a medical profile first.")

        # If changing profile, check limit
        if serializer.instance.profile != profile:
            if profile.emergency_contacts.count() >= 2:
                from rest_framework.exceptions import ValidationError

                raise ValidationError(
                    {"detail": "Maximum of 2 emergency contacts allowed."}
                )

        serializer.save()


class MedicalEventViewSet(viewsets.ModelViewSet):
    """ViewSet for MedicalEvent - CRUD operations."""

    queryset = MedicalEvent.objects.all()
    serializer_class = MedicalEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MedicalEvent.objects.filter(profile__user=self.request.user)

    def perform_create(self, serializer):
        try:
            profile = self.request.user.medical_profile
        except MedicalProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound("Please create a medical profile first.")
        serializer.save(profile=profile)


@extend_schema(
    methods=["GET"],
    parameters=[
        OpenApiParameter(
            name="public_id",
            location=OpenApiParameter.PATH,
            type=str,
            description="UUID of the medical profile",
        )
    ],
    responses=EmergencyProfileSerializer,
)
@api_view(["GET"])
@require_http_methods(["GET"])  # Explicitly allow only GET
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="20/m", method="GET")  # Reduced from 30/m
@ratelimit(key="ip", rate="100/h", method="GET")  # Add hourly limit
def emergency_scan_view(request, public_id):
    """
    Public emergency view - triggered by scanning NFC/QR code.
    Returns life-saving data WITHOUT requiring authentication.
    Excludes sensitive insurance/financial data.

    Rate limited to 20 requests per minute per IP to prevent abuse.
    """
    import logging

    logger = logging.getLogger(__name__)

    # Check for suspicious access patterns
    ip = request.META.get("REMOTE_ADDR")
    from django.core.cache import cache

    # Use both IP and user ID for cache key when available
    cache_key = f"emergency_scan_attempts_{ip}"
    if request.user.is_authenticated:
        cache_key = f"emergency_scan_{request.user.id}_{ip}"

    attempts = cache.get(cache_key, 0)

    if attempts > 50:  # More than 50 different profiles in 1 hour
        logger.warning(f"Suspicious emergency scan pattern from IP {ip}")

    try:
        profile = MedicalProfile.objects.select_related("user").get(public_id=public_id)
    except MedicalProfile.DoesNotExist:
        return Response(
            {"error": "Medical profile not found."}, status=status.HTTP_404_NOT_FOUND
        )

    cache.set(cache_key, attempts + 1, 3600)  # Expire after 1 hour

    # Also update the simple IP-based counter for backward compatibility
    if request.user.is_authenticated:
        ip_cache_key = f"emergency_scan_attempts_{ip}"
        cache.set(ip_cache_key, cache.get(ip_cache_key, 0) + 1, 3600)

    # Log access for security monitoring
    logger.info(f"Emergency scan from IP {ip} for profile {public_id}")

    # Log the access for audit trail
    ProfileAccessLog.objects.create(
        profile=profile,
        accessed_by=None,
        access_role="anonymous",
        access_type="emergency",
        ip_address=ip,
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
    )

    serializer = EmergencyProfileSerializer(profile)
    return Response(serializer.data)


@extend_schema(
    methods=["GET"],
    parameters=[
        OpenApiParameter(
            name="public_id",
            location=OpenApiParameter.PATH,
            type=str,
            description="UUID of the medical profile",
        )
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "access_granted": {"type": "boolean"},
                "user_role": {"type": "string"},
                "show_full_medical": {"type": "boolean"},
                "show_engineer_info": {"type": "boolean"},
                "show_insurance": {"type": "boolean"},
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="30/m", method="GET")
def emergency_access_check(request, public_id):
    """
    Check access level for emergency info.
    Returns what data the user is allowed to see based on their role.
    For anonymous users, returns basic access (user role).
    For authenticated users, returns access based on their profile_role.

    SECURITY: Insurance data is only returned after verifying actual doctor credentials.
    """
    from .models import ProfileAccessLog

    try:
        profile = MedicalProfile.objects.select_related("user").get(public_id=public_id)
    except MedicalProfile.DoesNotExist:
        return Response(
            {"error": "Medical profile not found."}, status=status.HTTP_404_NOT_FOUND
        )

    # Get user role - default to 'user' for anonymous
    user_role = get_user_role(request.user)
    is_verified_doctor = False

    if request.user.is_authenticated:
        # Verify actual doctor credentials for insurance access
        if user_role == "doctor":
            # Check if doctor has verified license number
            if hasattr(request.user, "license_number") and request.user.license_number:
                is_verified_doctor = getattr(request.user, "is_approved_doctor", False)

    # Determine access levels
    show_full_medical = user_role in ["doctor", "admin"]
    show_engineer_info = user_role in ["engineer", "admin"]
    # Only show insurance to VERIFIED doctors (not just any doctor role)
    show_insurance = is_verified_doctor or user_role in ["admin"]

    response_data = {
        "access_granted": True,
        "user_role": user_role,
        "show_full_medical": show_full_medical,
        "show_engineer_info": show_engineer_info,
        "show_insurance": show_insurance,
    }

    # Add medical history if authorized
    if show_full_medical:
        events = profile.medical_events.all()
        response_data["medical_events"] = MedicalEventSerializer(events, many=True).data
        response_data["chronic_diseases"] = profile.chronic_diseases

    # Add insurance info ONLY if verified doctor
    if show_insurance:
        response_data["insurance_provider"] = profile.insurance_provider
        response_data["insurance_number"] = profile.insurance_number

    # Add owner info if authorized
    if show_engineer_info:
        response_data["owner_name"] = (
            profile.user.get_full_name() or profile.user.username
        )
        response_data["owner_dob"] = profile.user.date_of_birth
        response_data["owner_phone"] = profile.user.phone_number
        if profile.user.national_id:
            nat_id = profile.user.national_id
            # Show only last 4 digits for security (show as: ****-****-****-XXXX)
            response_data["national_id_masked"] = f"****-****-****-{nat_id[-4:]}"

    # Log access for audit trail
    if request.user.is_authenticated:
        ProfileAccessLog.objects.create(
            profile=profile,
            accessed_by=request.user,
            access_role=user_role,
            access_type="api",
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )

    return Response(response_data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@ratelimit(key="ip", rate="10/m", method="POST")
def reveal_all_data_view(request, public_id):
    """
    API endpoint to reveal all medical data for a profile.
    Only allows access if the requesting user is:
    - A verified doctor (profile_role = 'doctor' and is_approved_doctor = True)
    - The profile owner (the user who owns the medical profile)

    This is used for the "Reveal All Data" button on the emergency page.
    """
    from .models import ProfileAccessLog

    try:
        profile = MedicalProfile.objects.select_related("user").get(public_id=public_id)
    except MedicalProfile.DoesNotExist:
        return Response(
            {"success": False, "message": "Medical profile not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Check if user is authenticated
    if not request.user.is_authenticated:
        return Response(
            {
                "success": False,
                "message": "Authentication required to reveal all data.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Get user role
    user_role = get_user_role(request.user)

    # Check if user is the profile owner
    # Note: request.user.medical_profile returns None (not exception) if not found
    is_profile_owner = (
        hasattr(request.user, "medical_profile")
        and request.user.medical_profile
        and request.user.medical_profile.public_id == profile.public_id
    )

    # Check if user is a verified doctor
    is_verified_doctor = False
    if user_role == "doctor":
        is_verified_doctor = getattr(request.user, "is_approved_doctor", False)

    # Only allow if doctor or owner
    if not is_verified_doctor and user_role != "admin" and not is_profile_owner:
        return Response(
            {
                "success": False,
                "message": "Only doctors or profile owners can reveal all data.",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # Log the access
    access_type = "doctor_reveal" if is_verified_doctor else "owner_reveal"
    ProfileAccessLog.objects.create(
        profile=profile,
        accessed_by=request.user,
        access_role=user_role,
        access_type=access_type,
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
    )

    return Response(
        {
            "success": True,
            "message": "Data revealed successfully.",
            "show_full_medical": True,
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def search_medical_data(request):
    """
    Search for medications or diagnoses.

    Query params:
    - q: Search query (required)
    - type: 'medications' or 'diagnoses' (optional, defaults to both)
    - lang: 'en' or 'ar' (optional, defaults to 'en')
    """
    query = request.GET.get("q", "").strip()
    data_type = request.GET.get("type", "both")  # medications, diagnoses, or both
    language = request.GET.get("lang", "en")

    if not query:
        return Response({"medications": [], "diagnoses": []})

    results = {}

    if data_type in ["medications", "both"]:
        results["medications"] = search_medications(query, language)

    if data_type in ["diagnoses", "both"]:
        results["diagnoses"] = search_diagnoses(query, language)

    return Response(results)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@ratelimit(key="ip", rate="10/m", method="GET")
def serve_insurance_image(request, public_id):
    """
    Serve decrypted insurance image for authorized users only.
    Only the profile owner or verified doctors can access insurance images.
    """
    from django.conf import settings
    from cryptography.fernet import Fernet
    import tempfile
    import os

    try:
        profile = MedicalProfile.objects.select_related("user").get(public_id=public_id)
    except MedicalProfile.DoesNotExist:
        raise Http404("Medical profile not found.")

    # Check authorization: owner or verified doctor
    user_role = getattr(request.user, "profile_role", "user")
    is_owner = profile.user == request.user
    is_verified_doctor = False

    if user_role == "doctor" and hasattr(request.user, "license_number"):
        is_verified_doctor = getattr(request.user, "is_approved_doctor", False)

    if not (is_owner or is_verified_doctor or request.user.is_staff):
        from rest_framework.exceptions import PermissionDenied

        raise PermissionDenied("You are not authorized to view this insurance image.")

    # Check if insurance image exists
    if not profile.insurance_image:
        raise Http404("No insurance image found.")

    # Check if it's encrypted
    if profile._is_encrypted():
        # Decrypt the image
        fernet_key = settings.FERNET_KEY.encode() if settings.FERNET_KEY else None
        if not fernet_key:
            raise Http404("Encryption key not configured.")

        f = Fernet(fernet_key)

        try:
            with profile.insurance_image.open("rb") as encrypted_file:
                encrypted_data = encrypted_file.read()

            decrypted_data = f.decrypt(encrypted_data)

            # Create temporary file to serve
            suffix = os.path.splitext(profile.insurance_image.name)[1] or ".jpg"
            with tempfile.NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
                tmp.write(decrypted_data)
                tmp_path = tmp.name

            # Determine content type
            content_types = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".pdf": "application/pdf",
            }
            content_type = content_types.get(suffix.lower(), "application/octet-stream")

            # Log access
            from .models import ProfileAccessLog

            ProfileAccessLog.objects.create(
                profile=profile,
                accessed_by=request.user,
                access_role=user_role,
                access_type="api",
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            )

            try:
                return FileResponse(
                    open(tmp_path, "rb"),
                    content_type=content_type,
                    as_attachment=False,
                    filename=f"insurance{suffix}",
                )
            finally:
                # Ensure temp file is cleaned up after serving
                import os

                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
        except Exception as e:
            logger.error(f"Failed to decrypt insurance image: {e}")
            raise Http404("Failed to decrypt insurance image.")
    else:
        # Not encrypted - serve directly
        return FileResponse(
            profile.insurance_image.open("rb"), content_type="image/jpeg"
        )
