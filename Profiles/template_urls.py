"""URL configuration for template views."""
from django.urls import path
from . import template_views

urlpatterns = [
    path('dashboard/', template_views.dashboard_view, name='dashboard'),
    path('profile/edit/', template_views.profile_edit_view, name='profile-edit'),
    path('medications/', template_views.medications_view, name='medications'),
    path('medications/add/', template_views.medication_add_view, name='medication-add'),
    path('contacts/', template_views.contacts_view, name='contacts'),
    path('contacts/add/', template_views.contact_add_view, name='contact-add'),
    path('events/', template_views.events_view, name='events'),
    path('events/add/', template_views.event_add_view, name='event-add'),
    # Emergency scan - HTML version for QR/NFC scanning
    path('emergency/<uuid:public_id>/', template_views.emergency_scan_template_view, name='emergency-scan-html'),
]
