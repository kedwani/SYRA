"""
Cache utilities for SYRA.
Provides Redis caching helpers for high-performance emergency access.
"""

from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """
    Cache service for managing Redis cache operations.
    """
    
    @staticmethod
    def get_emergency_critical(qr_token: str) -> dict | None:
        """
        Get cached critical emergency data.
        
        Args:
            qr_token: The QR token identifier
            
        Returns:
            Cached data or None if not found
        """
        key = f"emergency:critical:{qr_token}"
        try:
            return cache.get(key)
        except Exception as e:
            logger.error(f"Cache error for critical: {e}")
            return None
    
    @staticmethod
    def set_emergency_critical(qr_token: str, data: dict, ttl: int = 300) -> bool:
        """
        Cache critical emergency data.
        
        Args:
            qr_token: The QR token identifier
            data: Emergency data to cache
            ttl: Time to live in seconds (default 5 minutes)
            
        Returns:
            True if successful
        """
        key = f"emergency:critical:{qr_token}"
        try:
            cache.set(key, data, ttl)
            return True
        except Exception as e:
            logger.error(f"Cache set error for critical: {e}")
            return False
    
    @staticmethod
    def get_emergency_extended(qr_token: str) -> dict | None:
        """Get cached extended emergency data."""
        key = f"emergency:extended:{qr_token}"
        try:
            return cache.get(key)
        except Exception as e:
            logger.error(f"Cache error for extended: {e}")
            return None
    
    @staticmethod
    def set_emergency_extended(qr_token: str, data: dict, ttl: int = 300) -> bool:
        """Cache extended emergency data."""
        key = f"emergency:extended:{qr_token}"
        try:
            cache.set(key, data, ttl)
            return True
        except Exception as e:
            logger.error(f"Cache set error for extended: {e}")
            return False
    
    @staticmethod
    def invalidate_emergency_cache(qr_token: str) -> bool:
        """
        Invalidate all emergency cache for a QR token.
        
        Args:
            qr_token: The QR token identifier
            
        Returns:
            True if successful
        """
        keys = [
            f"emergency:critical:{qr_token}",
            f"emergency:extended:{qr_token}",
        ]
        try:
            cache.delete_many(keys)
            return True
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return False
    
    @staticmethod
    def get_user_profile(user_id: str) -> dict | None:
        """Get cached user profile."""
        key = f"user:profile:{user_id}"
        try:
            return cache.get(key)
        except Exception as e:
            logger.error(f"Cache error for profile: {e}")
            return None
    
    @staticmethod
    def set_user_profile(user_id: str, data: dict, ttl: int = 3600) -> bool:
        """Cache user profile (default 1 hour)."""
        key = f"user:profile:{user_id}"
        try:
            cache.set(key, data, ttl)
            return True
        except Exception as e:
            logger.error(f"Cache set error for profile: {e}")
            return False
    
    @staticmethod
    def invalidate_user_cache(user_id: str) -> bool:
        """Invalidate user cache."""
        key = f"user:profile:{user_id}"
        try:
            cache.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return False
    
    @staticmethod
    def get_rate_limit_key(identifier: str, endpoint: str) -> str:
        """Generate rate limit cache key."""
        return f"ratelimit:{endpoint}:{identifier}"
    
    @staticmethod
    def check_rate_limit(identifier: str, endpoint: str, limit: int, window: int) -> bool:
        """
        Check if rate limit is exceeded.
        
        Args:
            identifier: User/IP identifier
            endpoint: API endpoint
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            True if within limit, False if exceeded
        """
        key = CacheService.get_rate_limit_key(identifier, endpoint)
        try:
            current = cache.get(key, 0)
            if current >= limit:
                return False
            
            # Increment counter
            cache.set(key, current + 1, window)
            return True
        except Exception:
            # If cache fails, allow the request
            return True


# Singleton instance
cache_service = CacheService()