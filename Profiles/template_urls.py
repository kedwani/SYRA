"""URL configuration for template views."""

from django.urls import path
from . import template_views

urlpatterns = [
    path("dashboard/", template_views.dashboard_view, name="dashboard"),
    path("profile/edit/", template_views.profile_edit_view, name="profile-edit"),
    path(
        "profile/edit/medical/",
        template_views.profile_edit_view,
        name="profile-edit-medical",
    ),
    path(
        "profile/edit/personal/",
        template_views.personal_profile_edit_view,
        name="profile-edit-personal",
    ),
    path("medications/", template_views.medications_view, name="medications"),
    path("medications/add/", template_views.medication_add_view, name="medication-add"),
    path(
        "medications/<int:medication_id>/edit/",
        template_views.medication_edit_view,
        name="medication-edit",
    ),
    path(
        "medications/<int:medication_id>/delete/",
        template_views.medication_delete_view,
        name="medication-delete",
    ),
    path("contacts/", template_views.contacts_view, name="emergency-contacts"),
    path("contacts/add/", template_views.contact_add_view, name="contact-add"),
    path(
        "contacts/<int:contact_id>/edit/",
        template_views.contact_edit_view,
        name="contact-edit",
    ),
    path(
        "contacts/<int:contact_id>/delete/",
        template_views.contact_delete_view,
        name="contact-delete",
    ),
    path("events/", template_views.events_view, name="events"),
    path("events/add/", template_views.event_add_view, name="event-add"),
    path(
        "events/<int:event_id>/edit/", template_views.event_edit_view, name="event-edit"
    ),
    path(
        "events/<int:event_id>/delete/",
        template_views.event_delete_view,
        name="event-delete",
    ),
    # Emergency scan - HTML version for QR/NFC scanning
    path(
        "emergency/<uuid:public_id>/",
        template_views.emergency_scan_template_view,
        name="emergency-scan-html",
    ),
    # Emergency alert endpoint
    path(
        "emergency/alert/",
        template_views.emergency_alert_view,
        name="emergency-alert",
    ),
    # HTMX partial endpoints for fast loading
    path(
        "emergency/<uuid:public_id>/medications/",
        template_views.htmx_emergency_medications,
        name="emergency-medications-htmx",
    ),
    path(
        "emergency/<uuid:public_id>/contacts/",
        template_views.htmx_emergency_contacts,
        name="emergency-contacts-htmx",
    ),
    path(
        "emergency/<uuid:public_id>/history/",
        template_views.htmx_emergency_history,
        name="emergency-history-htmx",
    ),
    path(
        "emergency/<uuid:public_id>/physical/",
        template_views.htmx_emergency_physical,
        name="emergency-physical-htmx",
    ),
    # Doctor Portal
    path(
        "doctor/portal/",
        template_views.doctor_portal_view,
        name="doctor-portal",
    ),
    path(
        "doctor/add-event/<uuid:public_id>/",
        template_views.doctor_add_medical_event,
        name="doctor-add-event",
    ),
    path(
        "doctor/add-medication/<uuid:public_id>/",
        template_views.doctor_add_medication,
        name="doctor-add-medication",
    ),
    # User Approval Views
    path(
        "pending-approvals/",
        template_views.pending_approvals_view,
        name="pending-approvals",
    ),
    path(
        "approve-item/",
        template_views.approve_item_view,
        name="approve-item",
    ),
    path(
        "reject-item/",
        template_views.reject_item_view,
        name="reject-item",
    ),
]
