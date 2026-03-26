"""
JWT Authentication for SYRA.
Custom JWT token handling with access and refresh tokens.
"""

import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework import authentication, exceptions
from apps.accounts.models import User


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Custom JWT Authentication.
    Supports access tokens (short-lived) and refresh tokens.
    """
    
    keyword = 'Bearer'
    
    def authenticate(self, request):
        """Authenticate the request and return (user, token)."""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
        
        try:
            prefix, token = auth_header.split(' ')
            if prefix != self.keyword:
                return None
        except ValueError:
            return None
        
        return self._authenticate_credentials(token)
    
    def _authenticate_credentials(self, token: str) -> tuple:
        """
        Validate the token and return the user.
        
        Args:
            token: JWT access token
            
        Returns:
            Tuple of (User, token)
            
        Raises:
            exceptions.AuthenticationFailed: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        
        user_id = payload.get('user_id')
        if not user_id:
            raise exceptions.AuthenticationFailed('Invalid token payload')
        
        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')
        
        return (user, token)
    
    @staticmethod
    def generate_access_token(user: User) -> str:
        """Generate a short-lived access token (15 minutes)."""
        payload = {
            'user_id': str(user.id),
            'username': user.username,
            'email': user.email,
            'type': 'access',
            'exp': datetime.utcnow() + settings.JWT_ACCESS_TOKEN_LIFETIME,
            'iat': datetime.utcnow(),
        }
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
    
    @staticmethod
    def generate_refresh_token(user: User) -> str:
        """Generate a long-lived refresh token (7 days)."""
        payload = {
            'user_id': str(user.id),
            'type': 'refresh',
            'exp': datetime.utcnow() + settings.JWT_REFRESH_TOKEN_LIFETIME,
            'iat': datetime.utcnow(),
        }
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
    
    @staticmethod
    def verify_refresh_token(token: str) -> dict:
        """Verify a refresh token and return the payload."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            if payload.get('type') != 'refresh':
                raise exceptions.AuthenticationFailed('Invalid token type')
            
            return payload
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Refresh token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid refresh token')
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        """
        Generate a new access token from a refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token
        """
        payload = JWTAuthentication.verify_refresh_token(refresh_token)
        
        try:
            user = User.objects.get(id=payload.get('user_id'), is_active=True)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')
        
        return JWTAuthentication.generate_access_token(user)