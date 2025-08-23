"""Cache service for managing Redis operations."""

import json
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime

from app.cache import (
    get_cached_entitlements,
    set_cached_entitlements,
    delete_cached_entitlements,
    calculate_etag,
)
from app.config import settings


class CacheService:
    """Service for managing cache operations."""
    
    @staticmethod
    async def get_entitlements(tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get cached entitlements for tenant."""
        return await get_cached_entitlements(tenant_id)
    
    @staticmethod
    async def set_entitlements(tenant_id: str, data: Dict[str, Any], ttl: int = None) -> None:
        """Set cached entitlements for tenant."""
        await set_cached_entitlements(tenant_id, data, ttl)
    
    @staticmethod
    async def delete_entitlements(tenant_id: str) -> None:
        """Delete cached entitlements for tenant."""
        await delete_cached_entitlements(tenant_id)
    
    @staticmethod
    def calculate_etag(data: Dict[str, Any]) -> str:
        """Calculate ETag from entitlements data."""
        return calculate_etag(data)
    
    @staticmethod
    def get_cache_ttl() -> int:
        """Get cache TTL in seconds."""
        return settings.cache_ttl_seconds
