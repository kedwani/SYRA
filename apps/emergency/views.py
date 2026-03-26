"""
Views for SYRA emergency app.
High-performance public endpoints for emergency access via QR codes.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.profiles.models import MedicalProfile
from apps.medical.models import Allergy, Medication, Condition, EmergencyContact
from apps.common.cache import cache_service


class EmergencyCriticalView(APIView):
    """
    Public emergency endpoint - returns critical data only.
    This is the fastest endpoint, optimized for first-responders.
    
    GET /e/{qr_hash}/critical/
    """
    permission_classes = [AllowAny]
    
    def get(self, request, qr_hash):
        # Try cache first
        cached_data = cache_service.get_emergency_critical(qr_hash)
        if cached_data:
            return Response(cached_data)
        
        # Get profile
        profile = get_object_or_404(
            MedicalProfile,
            qr_token_hash=qr_hash,
            is_active=True
        )
        
        # Update last accessed
        profile.last_accessed_at = timezone.now()
        profile.save(update_fields=['last_accessed_at'])
        
        # Get critical data
        user = profile.user
        
        # Get severe/life-threatening allergies
        allergies = list(Allergy.objects.filter(
            profile=profile,
            severity__in=['severe', 'life_threatening']
        ).values('name', 'severity'))
        
        # Get critical conditions
        conditions = list(Condition.objects.filter(
            profile=profile,
            severity__in=['severe', 'life_threatening'],
            is_active=True
        ).values('name', 'severity'))
        
        data = {
            'blood_type': user.blood_type,
            'allergies': allergies,
            'critical_conditions': conditions,
            'emergency_note': profile.emergency_note,
            'last_updated': profile.updated_at.isoformat() if profile.updated_at else None,
        }
        
        # Cache for 5 minutes
        cache_service.set_emergency_critical(qr_hash, data, ttl=300)
        
        return Response(data)


class EmergencyExtendedView(APIView):
    """
    Extended emergency endpoint - returns all visible data.
    For medical personnel with proper verification.
    
    GET /e/{qr_hash}/extended/
    """
    permission_classes = [AllowAny]
    
    def get(self, request, qr_hash):
        # Try cache first
        cached_data = cache_service.get_emergency_extended(qr_hash)
        if cached_data:
            return Response(cached_data)
        
        # Get profile
        profile = get_object_or_404(
            MedicalProfile,
            qr_token_hash=qr_hash,
            is_active=True
        )
        
        # Update last accessed
        profile.last_accessed_at = timezone.now()
        profile.save(update_fields=['last_accessed_at'])
        
        # Determine visibility based on request
        viewer_role = self._get_viewer_role(request)
        
        # Get user info
        user = profile.user
        user_data = {
            'full_name': user.get_full_name() or user.username,
            'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
            'blood_type': user.blood_type,
        }
        
        # Filter items based on visibility
        def filter_visible(queryset):
            if viewer_role == 'owner':
                return queryset
            return queryset.exclude(visibility='private')
        
        # Get allergies
        allergies = list(filter_visible(
            Allergy.objects.filter(profile=profile)
        ).values('name', 'severity', 'visibility'))
        
        # Get medications
        medications = list(filter_visible(
            Medication.objects.filter(profile=profile, is_active=True)
        ).values('name', 'dosage', 'frequency', 'visibility'))
        
        # Get conditions
        conditions = list(filter_visible(
            Condition.objects.filter(profile=profile, is_active=True)
        ).values('name', 'severity', 'visibility'))
        
        # Get emergency contacts (always visible)
        emergency_contacts = list(EmergencyContact.objects.filter(
            profile=profile
        ).values('name', 'relationship', 'phone', 'email'))
        
        data = {
            'profile': user_data,
            'allergies': allergies,
            'medications': medications,
            'conditions': conditions,
            'emergency_contacts': emergency_contacts,
            'emergency_note': profile.emergency_note,
            'last_updated': profile.updated_at.isoformat() if profile.updated_at else None,
        }
        
        # Cache for 5 minutes
        cache_service.set_emergency_extended(qr_hash, data, ttl=300)
        
        return Response(data)
    
    def _get_viewer_role(self, request) -> str:
        """Determine the viewer role based on request."""
        # Check if user is authenticated and is the profile owner
        if request.user.is_authenticated:
            try:
                profile = MedicalProfile.objects.get(qr_token_hash=self.kwargs['qr_hash'])
                if profile.user == request.user:
                    return 'owner'
            except MedicalProfile.DoesNotExist:
                pass
            
            # Check if medical personnel
            if request.user.is_medical_personnel:
                return 'medical'
        
        return 'public'


class EmergencyPublicView(APIView):
    """
    Basic public emergency view.
    Returns minimal info visible to anyone.
    
    GET /e/{qr_hash}/
    """
    permission_classes = [AllowAny]
    
    def get(self, request, qr_hash):
        profile = get_object_or_404(
            MedicalProfile,
            qr_token_hash=qr_hash,
            is_active=True
        )
        
        # Update last accessed
        profile.last_accessed_at = timezone.now()
        profile.save(update_fields=['last_accessed_at'])
        
        user = profile.user
        
        return Response({
            'name': user.get_full_name() or user.username,
            'blood_type': user.blood_type,
            'emergency_note': profile.emergency_note,
        })