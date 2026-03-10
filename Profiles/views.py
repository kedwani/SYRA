"""Views for the Profiles app."""

from rest_framework import viewsets, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import MedicalProfile, Medication, EmergencyContact, MedicalEvent
from .serializers import (
    MedicalProfileSerializer,
    EmergencyProfileSerializer,
    MedicationSerializer,
    EmergencyContactSerializer,
    MedicalEventSerializer,
)


class MedicalProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for MedicalProfile - CRUD operations."""

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
        profile = MedicalProfile.objects.get(public_id=public_id)
    except MedicalProfile.DoesNotExist:
        return Response(
            {"error": "Medical profile not found."}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = EmergencyProfileSerializer(profile)
    return Response(serializer.data)
