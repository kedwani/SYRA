"""URL configuration for the Accounts API."""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # API endpoints
    path('register/', views.RegisterView.as_view(), name='api-register'),
    path('login/', views.login_view, name='api-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.profile_view, name='api-profile'),
]
