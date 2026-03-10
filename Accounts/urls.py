"""
Accounts/urls.py
----------------
URL routing for the Accounts app.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView, UserDetailView

urlpatterns = [
    # Registration
    path("register/", RegisterView.as_view(), name="register"),
    # JWT Login
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Current user info
    path("me/", UserDetailView.as_view(), name="user_detail"),
]
