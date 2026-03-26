"""
Views for SYRA medical app.
Handles CRUD operations for medical data (allergies, medications, conditions, emergency contacts).
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.profiles.models import MedicalProfile
from apps.medical.models import Allergy, Medication, Condition, EmergencyContact
from apps.medical.serializers import (
    AllergySerializer, MedicationSerializer, ConditionSerializer,
    EmergencyContactSerializer
)
from apps.common.cache import cache_service


class AllergyListCreateView(APIView):
    """List all allergies or create a new one."""
    permission_classes = [IsAuthenticated]
    
    def get_profile(self, request):
        profile, _ = MedicalProfile.objects.get_or_create(user=request.user)
        return profile
    
    def get(self, request):
        profile = self.get_profile(request)
        allergies = Allergy.objects.filter(profile=profile)
        serializer = AllergySerializer(allergies, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        profile = self.get_profile(request)
        serializer = AllergySerializer(data=request.data, context={'profile': profile})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache_service.invalidate_emergency_cache(str(profile.qr_token))
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AllergyDetailView(APIView):
    """Get, update, or delete a specific allergy."""
    permission_classes = [IsAuthenticated]
    
    def get_profile(self, request):
        return get_object_or_404(MedicalProfile, user=request.user)
    
    def get(self, request, pk):
        profile = self.get_profile(request)
        allergy = get_object_or_404(Allergy, pk=pk, profile=profile)
        serializer = AllergySerializer(allergy)
        return Response(serializer.data)
    
    def put(self, request, pk):
        profile = self.get_profile(request)
        allergy = get_object_or_404(Allergy, pk=pk, profile=profile)
        serializer = AllergySerializer(allergy, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache_service.invalidate_emergency_cache(str(profile.qr_token))
        return Response(serializer.data)
    
    def delete(self, request, pk):
        profile = self.get_profile(request)
        allergy = get_object_or_404(Allergy, pk=pk, profile=profile)
        allergy.delete()
        cache_service.invalidate_emergency_cache(str(profile.qr_token))
        return Response(status=status.HTTP_204_NO_CONTENT)


class MedicationListCreateView(APIView):
    """List all medications or create a new one."""
    permission_classes = [IsAuthenticated]
    
    def get_profile(self, request):
        profile, _ = MedicalProfile.objects.get_or_create(user=request.user)
        return profile
    
    def get(self, request):
        profile = self.get_profile(request)
        medications = Medication.objects.filter(profile=profile)
        serializer = MedicationSerializer(medications, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        profile = self.get_profile(request)
        serializer = MedicationSerializer(data=request.data, context={'profile': profile})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache_service.invalidate_emergency_cache(str(profile.qr_token))
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MedicationDetailView(APIView):
    """Get, update, or delete a specific medication."""
    permission_classes = [IsAuthenticated]
    
    def get_profile(self, request):
        return get_object_or_404(MedicalProfile, user=request.user)
    
    def get(self, request, pk):
        profile = self.get_profile(request)
        medication = get_object_or_404(Medication, pk=pk, profile=profile)
        serializer = MedicationSerializer(medication)
        return Response(serializer.data)
    
    def put(self, request, pk):
        profile = self.get_profile(request)
        medication = get_object_or_404(Medication, pk=pk, profile=profile)
        serializer = MedicationSerializer(medication, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache_service.invalidate_emergency_cache(str(profile.qr_token))
        return Response(serializer.data)
    
    def delete(self, request, pk):
        profile = self.get_profile(request)
        medication = get_object_or_404(Medication, pk=pk, profile=profile)
        medication.delete()
        cache_service.invalidate_emergency_cache(str(profile.qr_token))
        return Response(status=status.HTTP_204_NO_CONTENT)


class ConditionListCreateView(APIView):
    """List all conditions or create a new one."""
    permission_classes = [IsAuthenticated]
    
    def get_profile(self, request):
        profile, _ = MedicalProfile.objects.get_or_create(user=request.user)
        return profile
    
    def get(self, request):
        profile = self.get_profile(request)
        conditions = Condition.objects.filter(profile=profile)
        serializer = ConditionSerializer(conditions, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        profile = self.get_profile(request)
        serializer = ConditionSerializer(data=request.data, context={'profile': profile})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache_service.invalidate_emergency_cache(str(profile.qr_token))
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConditionDetailView(APIView):
    """Get, update, or delete a specific condition."""
    permission_classes = [IsAuthenticated]
    
    def get_profile(self, request):
        return get_object_or_404(MedicalProfile, user=request.user)
    
    def get(self, request, pk):
        profile = self.get_profile(request)
        condition = get_object_or_404(Condition, pk=pk, profile=profile)
        serializer = ConditionSerializer(condition)
        return Response(serializer.data)
    
    def put(self, request, pk):
        profile = self.get_profile(request)
        condition = get_object_or_404(Condition, pk=pk, profile=profile)
        serializer = ConditionSerializer(condition, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache_service.invalidate_emergency_cache(str(profile.qr_token))
        return Response(serializer.data)
    
    def delete(self, request, pk):
        profile = self.get_profile(request)
        condition = get_object_or_404(Condition, pk=pk, profile=profile)
        condition.delete()
        cache_service.invalidate_emergency_cache(str(profile.qr_token))
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmergencyContactListCreateView(APIView):
    """List all emergency contacts or create a new one."""
    permission_classes = [IsAuthenticated]
    
    def get_profile(self, request):
        profile, _ = MedicalProfile.objects.get_or_create(user=request.user)
        return profile
    
    def get(self, request):
        profile = self.get_profile(request)
        contacts = EmergencyContact.objects.filter(profile=profile)
        serializer = EmergencyContactSerializer(contacts, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        profile = self.get_profile(request)
        serializer = EmergencyContactSerializer(data=request.data, context={'profile': profile})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EmergencyContactDetailView(APIView):
    """Get, update, or delete a specific emergency contact."""
    permission_classes = [IsAuthenticated]
    
    def get_profile(self, request):
        return get_object_or_404(MedicalProfile, user=request.user)
    
    def get(self, request, pk):
        profile = self.get_profile(request)
        contact = get_object_or_404(EmergencyContact, pk=pk, profile=profile)
        serializer = EmergencyContactSerializer(contact)
        return Response(serializer.data)
    
    def put(self, request, pk):
        profile = self.get_profile(request)
        contact = get_object_or_404(EmergencyContact, pk=pk, profile=profile)
        serializer = EmergencyContactSerializer(contact, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def delete(self, request, pk):
        profile = self.get_profile(request)
        contact = get_object_or_404(EmergencyContact, pk=pk, profile=profile)
        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)