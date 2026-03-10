"""
Profiles/urls.py
----------------
URL routing for all profile-related endpoints.
"""

from django.urls import path

from .views import (
    EmergencyContactDetailView,
    EmergencyContactListCreateView,
    InsuranceView,
    MedicalEventDetailView,
    MedicalEventListCreateView,
    MedicalProfileView,
    MedicationDetailView,
    MedicationListCreateView,
    PatientSearchView,
)

urlpatterns = [
    # ---- Search (must come before <username> to avoid collision) ----
    path("search/", PatientSearchView.as_view(), name="patient-search"),
    # ---- Main profile ----
    path("<str:username>/", MedicalProfileView.as_view(), name="medical-profile"),
    # ---- Insurance (sensitive — owner only) ----
    path("<str:username>/insurance/", InsuranceView.as_view(), name="insurance"),
    # ---- Emergency contacts ----
    path(
        "<str:username>/contacts/",
        EmergencyContactListCreateView.as_view(),
        name="contacts-list",
    ),
    path(
        "<str:username>/contacts/<int:pk>/",
        EmergencyContactDetailView.as_view(),
        name="contacts-detail",
    ),
    # ---- Medications ----
    path(
        "<str:username>/medications/",
        MedicationListCreateView.as_view(),
        name="medications-list",
    ),
    path(
        "<str:username>/medications/<int:pk>/",
        MedicationDetailView.as_view(),
        name="medications-detail",
    ),
    # ---- Medical history ----
    path(
        "<str:username>/history/",
        MedicalEventListCreateView.as_view(),
        name="history-list",
    ),
    path(
        "<str:username>/history/<int:pk>/",
        MedicalEventDetailView.as_view(),
        name="history-detail",
    ),
]
