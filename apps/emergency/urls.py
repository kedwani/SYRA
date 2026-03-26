"""
URL configuration for SYRA emergency app.
Public emergency access endpoints.
"""

from django.urls import path
from apps.emergency import views

app_name = 'emergency'

urlpatterns = [
    # Public emergency access endpoints
    path('<str:qr_hash>/', views.EmergencyPublicView.as_view(), name='emergency-public'),
    path('<str:qr_hash>/critical/', views.EmergencyCriticalView.as_view(), name='emergency-critical'),
    path('<str:qr_hash>/extended/', views.EmergencyExtendedView.as_view(), name='emergency-extended'),
]