"""
URL configuration for SYRA project.
API version 1 endpoints.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import ViewSets
from apps.accounts.views import RegisterView, LoginView, RefreshTokenView, LogoutView, MeView, ChangePasswordView
from apps.profiles.views import (
    MyProfileView, QRCodeView, QRCodeRotateView, PublicProfileView,
    ProfileVisibilityView, ProfileEmergencyNoteView
)
from apps.medical.views import (
    AllergyListCreateView, AllergyDetailView,
    MedicationListCreateView, MedicationDetailView,
    ConditionListCreateView, ConditionDetailView,
    EmergencyContactListCreateView, EmergencyContactDetailView
)
from apps.emergency.views import EmergencyCriticalView, EmergencyExtendedView, EmergencyPublicView
from apps.hardware.views import BraceletClaimView, BraceletListView, BraceletStatusView, BraceletActionView
from apps.store.views import ProductListView, ProductDetailView, OrderListView, OrderDetailView, OrderCancelView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include([
        # Auth endpoints
        path('auth/register/', RegisterView.as_view(), name='register'),
        path('auth/login/', LoginView.as_view(), name='login'),
        path('auth/refresh/', RefreshTokenView.as_view(), name='refresh'),
        path('auth/logout/', LogoutView.as_view(), name='logout'),
        path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
        
        # Profile endpoints
        path('profiles/me/', MyProfileView.as_view(), name='my-profile'),
        path('profiles/me/visibility/', ProfileVisibilityView.as_view(), name='profile-visibility'),
        path('profiles/me/emergency-note/', ProfileEmergencyNoteView.as_view(), name='profile-emergency-note'),
        path('profiles/qr/', QRCodeView.as_view(), name='qr-code'),
        path('profiles/qr/rotate/', QRCodeRotateView.as_view(), name='qr-rotate'),
        path('profiles/<str:qr_id>/', PublicProfileView.as_view(), name='public-profile'),
        
        # Medical data endpoints - manually defined to avoid router issues
        path('medical/allergies/', AllergyListCreateView.as_view(), name='allergy-list'),
        path('medical/allergies/<int:pk>/', AllergyDetailView.as_view(), name='allergy-detail'),
        path('medical/medications/', MedicationListCreateView.as_view(), name='medication-list'),
        path('medical/medications/<int:pk>/', MedicationDetailView.as_view(), name='medication-detail'),
        path('medical/conditions/', ConditionListCreateView.as_view(), name='condition-list'),
        path('medical/conditions/<int:pk>/', ConditionDetailView.as_view(), name='condition-detail'),
        path('medical/emergency-contacts/', EmergencyContactListCreateView.as_view(), name='emergency-contact-list'),
        path('medical/emergency-contacts/<int:pk>/', EmergencyContactDetailView.as_view(), name='emergency-contact-detail'),
        
        # Emergency endpoints (public - no auth)
        path('e/<str:qr_hash>/', EmergencyPublicView.as_view(), name='emergency-public'),
        path('e/<str:qr_hash>/critical/', EmergencyCriticalView.as_view(), name='emergency-critical'),
        path('e/<str:qr_hash>/extended/', EmergencyExtendedView.as_view(), name='emergency-extended'),
        
        # Hardware/Bracelets
        path('bracelets/', BraceletListView.as_view(), name='bracelet-list'),
        path('bracelets/claim/', BraceletClaimView.as_view(), name='bracelet-claim'),
        path('bracelets/status/<str:serial>/', BraceletStatusView.as_view(), name='bracelet-status'),
        path('bracelets/<int:pk>/lost/', BraceletActionView.as_view(), name='bracelet-lost'),
        path('bracelets/<int:pk>/suspend/', BraceletActionView.as_view(), name='bracelet-suspend'),
        
        # Products (public read-only)
        path('products/', ProductListView.as_view(), name='product-list'),
        path('products/<str:slug>/', ProductDetailView.as_view(), name='product-detail'),
        
        # Orders
        path('orders/', OrderListView.as_view(), name='order-list'),
        path('orders/<uuid:pk>/', OrderDetailView.as_view(), name='order-detail'),
        path('orders/<uuid:pk>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
    ])),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)