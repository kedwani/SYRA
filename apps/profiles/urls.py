"""
URL configuration for SYRA profiles app.
"""

from django.urls import path
from apps.profiles import views

app_name = 'profiles'

urlpatterns = [
    # Profile management
    path('me/', views.MyProfileView.as_view(), name='my-profile'),
    path('me/visibility/', views.ProfileVisibilityView.as_view(), name='profile-visibility'),
    path('me/emergency-note/', views.ProfileEmergencyNoteView.as_view(), name='profile-emergency-note'),
    
    # QR code
    path('qr/', views.QRCodeView.as_view(), name='qr-code'),
    path('qr/rotate/', views.QRCodeRotateView.as_view(), name='qr-rotate'),
    
    # Public profile (by QR hash)
    path('<str:qr_id>/', views.PublicProfileView.as_view(), name='public-profile'),
]