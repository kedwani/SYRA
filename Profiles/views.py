"""
Profiles/views.py
-----------------
API views for the Profiles app.

Endpoints overview:
  GET  /api/profile/<username>/             → Public medical profile (no insurance)
  PUT  /api/profile/<username>/             → Update general profile fields
  GET  /api/profile/<username>/insurance/   → Insurance data (authenticated owner only)
  PUT  /api/profile/<username>/insurance/   → Upload / update insurance card

  GET  /api/profile/<username>/contacts/          → List emergency contacts
  POST /api/profile/<username>/contacts/          → Add emergency contact
  PUT  /api/profile/<username>/contacts/<pk>/     → Update contact
  DELETE /api/profile/<username>/contacts/<pk>/   → Remove contact

  GET  /api/profile/<username>/medications/       → List medications
  POST /api/profile/<username>/medications/       → Add medication
  (PUT/DELETE similar)

  GET  /api/profile/<username>/history/           → Medical event history
  POST /api/profile/<username>/history/           → Add medical event

  GET  /api/profile/search/?q=<query>             → Search by username or public_id (QR)
"""

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EmergencyContact, MedicalEvent, MedicalProfile, Medication
from .serializers import (
    EmergencyContactSerializer,
    InsuranceSerializer,
    MedicalEventSerializer,
    MedicalProfileSerializer,
    MedicationSerializer,
)

User = get_user_model()


# ---------------------------------------------------------------------------
# Permissions helper
# ---------------------------------------------------------------------------


class IsProfileOwner(permissions.BasePermission):
    """Allow access only to the owner of the profile."""

    def has_object_permission(self, request, view, obj: MedicalProfile) -> bool:
        return obj.user == request.user


# ---------------------------------------------------------------------------
# Profile CRUD
# ---------------------------------------------------------------------------


class MedicalProfileView(generics.RetrieveUpdateAPIView):
    """
    GET  → anyone authenticated can read a profile (first-responder use case).
    PUT  → only the profile owner can update.
    Insurance data is explicitly excluded from this serializer.
    """

    serializer_class = MedicalProfileSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsProfileOwner()]

    def get_object(self) -> MedicalProfile:
        username = self.kwargs["username"]
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(MedicalProfile, user=user)
        self.check_object_permissions(self.request, profile)
        return profile


# ---------------------------------------------------------------------------
# Insurance — isolated sensitive endpoint (Phase 3)
# ---------------------------------------------------------------------------


class InsuranceView(generics.RetrieveUpdateAPIView):
    """
    GET /api/profile/<username>/insurance/
      Returns decrypted insurance card image (base64) + company name.
      Restricted to profile owner only.

    PUT /api/profile/<username>/insurance/
      Upload / replace the insurance card image.
    """

    serializer_class = InsuranceSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfileOwner]

    def get_object(self) -> MedicalProfile:
        username = self.kwargs["username"]
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(MedicalProfile, user=user)
        self.check_object_permissions(self.request, profile)
        return profile


# ---------------------------------------------------------------------------
# Emergency Contacts
# ---------------------------------------------------------------------------


class EmergencyContactListCreateView(generics.ListCreateAPIView):
    """List or add emergency contacts for a profile."""

    serializer_class = EmergencyContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _get_profile(self) -> MedicalProfile:
        username = self.kwargs["username"]
        user = get_object_or_404(User, username=username)
        return get_object_or_404(MedicalProfile, user=user)

    def get_queryset(self):
        return self._get_profile().emergency_contacts.all()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["profile"] = self._get_profile()
        return ctx

    def perform_create(self, serializer):
        serializer.save(profile=self._get_profile())


class EmergencyContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmergencyContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs["username"]
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(MedicalProfile, user=user)
        return profile.emergency_contacts.all()


# ---------------------------------------------------------------------------
# Medications
# ---------------------------------------------------------------------------


class MedicationListCreateView(generics.ListCreateAPIView):
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _get_profile(self) -> MedicalProfile:
        username = self.kwargs["username"]
        user = get_object_or_404(User, username=username)
        return get_object_or_404(MedicalProfile, user=user)

    def get_queryset(self):
        return self._get_profile().medications.all()

    def perform_create(self, serializer):
        serializer.save(profile=self._get_profile())


class MedicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs["username"]
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(MedicalProfile, user=user)
        return profile.medications.all()


# ---------------------------------------------------------------------------
# Medical History (events)
# ---------------------------------------------------------------------------


class MedicalEventListCreateView(generics.ListCreateAPIView):
    serializer_class = MedicalEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _get_profile(self) -> MedicalProfile:
        username = self.kwargs["username"]
        user = get_object_or_404(User, username=username)
        return get_object_or_404(MedicalProfile, user=user)

    def get_queryset(self):
        return self._get_profile().medical_history.all()

    def perform_create(self, serializer):
        serializer.save(profile=self._get_profile())


class MedicalEventDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MedicalEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs["username"]
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(MedicalProfile, user=user)
        return profile.medical_history.all()


# ---------------------------------------------------------------------------
# Search (Phase 3) — find patient by username or public QR/NFC UUID
# ---------------------------------------------------------------------------


class PatientSearchView(APIView):
    """
    GET /api/profile/search/?q=<query>

    Searches by:
      - username  (exact)
      - public_id (UUID used in QR codes / NFC tags)

    Returns a limited safe view of the matching profile.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs) -> Response:
        query = request.query_params.get("q", "").strip()

        if not query:
            return Response(
                {"detail": "Provide a search query via ?q="},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = (
            MedicalProfile.objects.select_related("user")
            .filter(user__username=query)
            .first()
            or MedicalProfile.objects.select_related("user")
            .filter(public_id=query)
            .first()
        )

        if not profile:
            return Response(
                {"detail": "No patient found for the given query."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = MedicalProfileSerializer(profile, context={"request": request})
        return Response(serializer.data)
