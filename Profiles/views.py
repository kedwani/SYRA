"""Views for the Profiles app."""

from rest_framework import viewsets, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
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


class MedicalProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for MedicalProfile - CRUD operations."""

    queryset = MedicalProfile.objects.all()
    permission_classes = [IsAuthenticated]

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
        return MedicalProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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
@permission_classes([AllowAny])
def emergency_scan_view(request, public_id):
    """
    Public emergency view - triggered by scanning NFC/QR code.
    Returns life-saving data WITHOUT requiring authentication.
    Excludes sensitive insurance/financial data.
    Returns JSON response for API consumers.
    """
    try:
        profile = MedicalProfile.objects.select_related("user").get(public_id=public_id)
    except MedicalProfile.DoesNotExist:
        return Response(
            {"error": "Medical profile not found."}, status=status.HTTP_404_NOT_FOUND
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
def emergency_access_check(request, public_id):
    """
    Check access level for emergency info.
    Returns what data the user is allowed to see based on their role.
    For anonymous users, returns basic access (user role).
    For authenticated users, returns access based on their profile_role.
    """
    try:
        profile = MedicalProfile.objects.select_related("user").get(public_id=public_id)
    except MedicalProfile.DoesNotExist:
        return Response(
            {"error": "Medical profile not found."}, status=status.HTTP_404_NOT_FOUND
        )

    # Get user role - default to 'user' for anonymous
    user_role = "user"
    if request.user.is_authenticated:
        user_role = getattr(request.user, "profile_role", "user")

    # Determine access levels
    show_full_medical = user_role in ["doctor", "admin"]
    show_engineer_info = user_role in ["engineer", "admin"]
    show_insurance = user_role in ["doctor", "admin", "engineer"]

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

    # Add insurance info if authorized
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
            # Only show last 4 digits for security
            response_data["national_id_masked"] = f"****{nat_id[-4:]}"

    return Response(response_data)


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
