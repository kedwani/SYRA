"""
Views for SYRA accounts app.
Handles authentication, registration, and user profile management.
"""

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.authentication import JWTAuthentication
from apps.accounts.serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    TokenResponseSerializer, ChangePasswordSerializer,
    MedicalPersonnelSerializer
)
from apps.accounts.models import User


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    
    POST /api/v1/auth/register/
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        access_token = JWTAuthentication.generate_access_token(user)
        refresh_token = JWTAuthentication.generate_refresh_token(user)
        
        return Response(
            {
                'access': access_token,
                'refresh': refresh_token,
                'user': UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    """
    User login endpoint.
    
    POST /api/v1/auth/login/
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request):
        from django.contrib.auth import authenticate
        
        email = request.data.get('email', '')
        password = request.data.get('password', '')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=email, password=password)
        
        if not user:
            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.is_active:
            return Response(
                {'error': 'User account is disabled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate tokens
        access_token = JWTAuthentication.generate_access_token(user)
        refresh_token = JWTAuthentication.generate_refresh_token(user)
        
        return Response({
            'access': access_token,
            'refresh': refresh_token,
            'user': UserSerializer(user).data
        })


class RefreshTokenView(APIView):
    """
    Refresh access token endpoint.
    
    POST /api/v1/auth/refresh/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            access_token = JWTAuthentication.refresh_access_token(refresh_token)
            return Response({'access': access_token})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    """
    User logout endpoint.
    
    POST /api/v1/auth/logout/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # In a stateless JWT system, logout is handled client-side
        # by removing the token. For token blacklist implementation,
        # you would add the token to a blacklist here.
        return Response({'message': 'Successfully logged out'})


class MeView(generics.RetrieveUpdateAPIView):
    """
    Current user profile endpoint.
    
    GET /api/v1/profiles/me/
    PUT /api/v1/profiles/me/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """
    Change password endpoint.
    
    POST /api/v1/auth/change-password/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': 'Password changed successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def medical_personnel_verify(request):
    """
    Verify medical personnel credentials.
    
    POST /api/v1/auth/verify-medical/
    """
    if request.method == 'GET':
        return Response({
            'is_medical_personnel': request.user.is_medical_personnel,
            'hospital_verified': request.user.hospital_verified
        })
    
    # POST - update medical personnel info
    serializer = MedicalPersonnelSerializer(
        instance=request.user,
        data=request.data,
        partial=True
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    return Response(serializer.data)