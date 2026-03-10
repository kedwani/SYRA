"""URL configuration for the Profiles API."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MedicalProfileViewSet, MedicationViewSet,
    EmergencyContactViewSet, MedicalEventViewSet,
    emergency_scan_view
)

router = DefaultRouter()
router.register(r'profiles', MedicalProfileViewSet, basename='medical-profile')
router.register(r'medications', MedicationViewSet, basename='medication')
router.register(r'contacts', EmergencyContactViewSet, basename='emergency-contact')
router.register(r'events', MedicalEventViewSet, basename='medical-event')

urlpatterns = [
    path('', include(router.urls)),
    path('scan/<uuid:public_id>/', emergency_scan_view, name='emergency-scan'),
]
