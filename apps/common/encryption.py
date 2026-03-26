"""
Encryption utilities for SYRA.
Provides field-level encryption for sensitive medical data.
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from django.conf import settings


class EncryptionService:
    """
    Field-level encryption service using Fernet (symmetric encryption).
    """
    
    _instance = None
    _fernet = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._fernet is None:
            self._initialize()
    
    def _initialize(self):
        """Initialize encryption with key from settings or environment."""
        # Get encryption key from settings or generate from secret
        key = getattr(settings, 'ENCRYPTION_KEY', None)
        
        if not key:
            # Generate key from Django secret key
            secret = settings.SECRET_KEY.encode()
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'syra_medical_data',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(secret))
        
        self._fernet = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt a string value.
        
        Args:
            data: Plain text string to encrypt
            
        Returns:
            Base64 encoded encrypted string
        """
        if not data:
            return ''
        
        encrypted = self._fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt an encrypted string.
        
        Args:
            encrypted_data: Base64 encoded encrypted string
            
        Returns:
            Decrypted plain text string
        """
        if not encrypted_data:
            return ''
        
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self._fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception:
            return ''
    
    def encrypt_dict(self, data: dict) -> dict:
        """
        Encrypt all string values in a dictionary.
        
        Args:
            data: Dictionary with potentially sensitive data
            
        Returns:
            Dictionary with sensitive fields encrypted
        """
        if not data:
            return {}
        
        encrypted = {}
        for key, value in data.items():
            if isinstance(value, str) and value:
                encrypted[key] = self.encrypt(value)
            else:
                encrypted[key] = value
        
        return encrypted
    
    def decrypt_dict(self, data: dict, fields: list) -> dict:
        """
        Decrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary with encrypted data
            fields: List of field names to decrypt
            
        Returns:
            Dictionary with specified fields decrypted
        """
        if not data:
            return {}
        
        decrypted = data.copy()
        for field in fields:
            if field in decrypted and decrypted[field]:
                decrypted[field] = self.decrypt(decrypted[field])
        
        return decrypted


# Singleton instance
encryption_service = EncryptionService()


def encrypt_medical_data(data: str) -> str:
    """Convenience function for encryption."""
    return encryption_service.encrypt(data)


def decrypt_medical_data(data: str) -> str:
    """Convenience function for decryption."""
    return encryption_service.decrypt(data)