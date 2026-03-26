"""
Views for SYRA profiles app.
Handles medical profile management and QR code generation.
"""

import uuid
import io
import base64
import qrcode
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.profiles.models import MedicalProfile
from apps.profiles.serializers import (
    MedicalProfileSerializer, ProfileVisibilitySerializer, QRCodeSerializer
)
from apps.common.cache import cache_service


class MyProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update current user's medical profile.
    
    GET /api/v1/profiles/me/
    PUT /api/v1/profiles/me/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MedicalProfileSerializer
    
    def get_object(self):
        profile, created = MedicalProfile.objects.get_or_create(
            user=self.request.user,
            defaults={'qr_token': uuid.uuid4()}
        )
        return profile
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Invalidate cache when profile is updated
        cache_service.invalidate_emergency_cache(str(instance.qr_token))
        
        return Response(serializer.data)


class QRCodeView(APIView):
    """
    Generate and retrieve QR code for user's profile.
    
    GET /api/v1/profiles/qr/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        profile = get_object_or_404(MedicalProfile, user=request.user)
        
        # Generate QR code image
        qr_url = f"{request.build_absolute_uri('/').rstrip('/')}/e/{profile.qr_token_hash}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_image = base64.b64encode(buffer.getvalue()).decode()
        
        return Response({
            'qr_token_hash': profile.qr_token_hash,
            'qr_url': qr_url,
            'qr_image': f"data:image/png;base64,{qr_image}"
        })


class QRCodeRotateView(APIView):
    """
    Rotate QR code for security.
    
    POST /api/v1/profiles/qr/rotate/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        profile = get_object_or_404(MedicalProfile, user=request.user)
        
        # Generate new QR token
        profile.qr_token = uuid.uuid4()
        profile.save()
        
        # Invalidate old cache
        cache_service.invalidate_emergency_cache(str(profile.qr_token))
        
        # Invalidate hardware bracelets
        from apps.hardware.models import Bracelet
        Bracelet.objects.filter(profile=profile).update(
            qr_token=profile.qr_token,
            status=Bracelet.STATUS_CLAIMED  # Re-require claim
        )
        
        return Response({
            'message': 'QR code rotated successfully',
            'qr_token_hash': profile.qr_token_hash
        })


class PublicProfileView(APIView):
    """
    Public profile view by QR token hash.
    
    GET /api/v1/profiles/{qr_id}/
    """
    permission_classes = [AllowAny]
    
    def get(self, request, qr_id):
        profile = get_object_or_404(
            MedicalProfile,
            qr_token_hash=qr_id,
            is_active=True
        )
        
        # Update last accessed
        from django.utils import timezone
        profile.last_accessed_at = timezone.now()
        profile.save(update_fields=['last_accessed_at'])
        
        # Get basic info (public visibility)
        return Response({
            'name': profile.user.get_full_name() or profile.user.username,
            'blood_type': profile.user.blood_type,
            'emergency_note': profile.emergency_note,
        })


class ProfileVisibilityView(APIView):
    """
    Update profile visibility settings.
    
    PUT /api/v1/profiles/me/visibility/
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        profile = get_object_or_404(MedicalProfile, user=request.user)
        serializer = ProfileVisibilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        profile.default_visibility = serializer.validated_data['default_visibility']
        profile.save()
        
        return Response({
            'default_visibility': profile.default_visibility
        })


class ProfileEmergencyNoteView(APIView):
    """
    Update profile emergency note.
    
    PUT /api/v1/profiles/me/emergency-note/
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        profile = get_object_or_404(MedicalProfile, user=request.user)
        
        emergency_note = request.data.get('emergency_note', '')
        profile.emergency_note = emergency_note[:500]  # Limit length
        profile.save()
        
        # Invalidate cache
        cache_service.invalidate_emergency_cache(str(profile.qr_token))
        
        return Response({
            'emergency_note': profile.emergency_note
        })