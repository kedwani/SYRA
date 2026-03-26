"""
Views for SYRA hardware app.
Handles bracelet management, claiming, and status.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.hardware.models import Bracelet
from apps.hardware.serializers import BraceletSerializer, BraceletClaimSerializer
from apps.profiles.models import MedicalProfile
from apps.common.cache import cache_service


class BraceletListView(APIView):
    """List user's linked bracelets."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        profile = get_object_or_404(MedicalProfile, user=request.user)
        bracelets = Bracelet.objects.filter(profile=profile)
        serializer = BraceletSerializer(bracelets, many=True)
        return Response(serializer.data)


class BraceletClaimView(APIView):
    """Claim a bracelet using serial number and PIN."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = BraceletClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        serial = serializer.validated_data['serial_number']
        pin = serializer.validated_data['claim_pin']
        
        bracelet = Bracelet.objects.filter(
            serial_number__iexact=serial,
            status=Bracelet.STATUS_UNCLAIMED
        ).first()
        
        if not bracelet:
            return Response(
                {'error': 'Bracelet not found or already claimed'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if bracelet.claim_pin != pin:
            return Response(
                {'error': 'Invalid claim PIN'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        profile = get_object_or_404(MedicalProfile, user=request.user)
        
        bracelet.profile = profile
        bracelet.status = Bracelet.STATUS_CLAIMED
        bracelet.save()
        
        profile.qr_token = bracelet.qr_token
        profile.save()
        
        cache_service.invalidate_emergency_cache(str(profile.qr_token))
        
        return Response({
            'message': 'Bracelet claimed successfully',
            'bracelet': BraceletSerializer(bracelet).data
        })


class BraceletStatusView(APIView):
    """Check bracelet linkage status."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, serial):
        bracelet = Bracelet.objects.filter(serial_number__iexact=serial).first()
        
        if not bracelet:
            return Response({'status': 'not_found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'serial_number': bracelet.serial_number,
            'status': bracelet.status,
            'is_claimed': bracelet.status != Bracelet.STATUS_UNCLAIMED,
        })


class BraceletActionView(APIView):
    """Mark bracelet as lost or suspend it."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        profile = get_object_or_404(MedicalProfile, user=request.user)
        bracelet = get_object_or_404(Bracelet, pk=pk, profile=profile)
        
        action = request.data.get('action', 'lost')
        
        if action == 'lost':
            if not bracelet.mark_lost():
                return Response(
                    {'error': 'Cannot mark bracelet as lost'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response({'message': 'Bracelet marked as lost'})
        
        elif action == 'suspend':
            bracelet.suspend()
            cache_service.invalidate_emergency_cache(str(profile.qr_token))
            return Response({'message': 'Bracelet suspended'})
        
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)