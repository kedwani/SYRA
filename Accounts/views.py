"""
Accounts/views.py
-----------------
Authentication endpoints: Register and retrieve user details.
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions

from .serializers import UserDetailSerializer, UserRegistrationSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Open endpoint — anyone can register.
    On success, a MedicalProfile is automatically created via Django signal.
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserDetailView(generics.RetrieveAPIView):
    """
    GET /api/auth/me/
    Returns the currently authenticated user's basic info.
    """

    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user
