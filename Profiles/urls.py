"""URL configuration for the Profiles API."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MedicalProfileViewSet,
    MedicationViewSet,
    EmergencyContactViewSet,
    MedicalEventViewSet,
    emergency_scan_view,
    emergency_access_check,
    search_medical_data,
    serve_insurance_image,
    reveal_all_data_view,
)
from .emergency_alerts import send_emergency_alert, get_nearby_hospitals

router = DefaultRouter()
router.register(r"profiles", MedicalProfileViewSet, basename="medical-profile")
router.register(r"medications", MedicationViewSet, basename="medication")
router.register(r"contacts", EmergencyContactViewSet, basename="emergency-contact")
router.register(r"events", MedicalEventViewSet, basename="medical-event")

urlpatterns = [
    path("", include(router.urls)),
    path("scan/<uuid:public_id>/", emergency_scan_view, name="emergency-scan"),
    path(
        "access/<uuid:public_id>/",
        emergency_access_check,
        name="emergency-access-check",
    ),
    path(
        "insurance-image/<uuid:public_id>/",
        serve_insurance_image,
        name="serve-insurance-image",
    ),
    path("alert/<uuid:public_id>/", send_emergency_alert, name="emergency-alert"),
    path("hospitals/", get_nearby_hospitals, name="nearby-hospitals"),
    path("search/", search_medical_data, name="search-medical-data"),
    path(
        "reveal-all-data/<uuid:public_id>/",
        reveal_all_data_view,
        name="reveal-all-data",
    ),
]
