"""Redis cache configuration and client."""

import json
import hashlib
from typing import Any, Optional

import redis.asyncio as redis
from app.config import settings

# Redis client
redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get Redis client."""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_keepalive=True,
        )
    return redis_client


async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


def calculate_etag(data: dict) -> str:
    """Calculate ETag from data."""
    # Convert datetime objects to ISO format strings for JSON serialization
    def serialize_datetime(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return obj
    
    content = json.dumps(data, sort_keys=True, separators=(",", ":"), default=serialize_datetime)
    return hashlib.sha256(content.encode()).hexdigest()


def get_cache_key(tenant_id: str) -> str:
    """Get cache key for tenant entitlements."""
    return f"rules:tenant:{tenant_id}:blob"


async def get_cached_entitlements(tenant_id: str) -> Optional[dict]:
    """Get cached entitlements for tenant."""
    try:
        redis_client = await get_redis()
        key = get_cache_key(tenant_id)
        data = await redis_client.get(key)
        return json.loads(data) if data else None
    except Exception:
        # Return None if Redis is not available (e.g., in tests)
        return None


async def set_cached_entitlements(tenant_id: str, data: dict, ttl: int = None) -> None:
    """Set cached entitlements for tenant."""
    try:
        redis_client = await get_redis()
        key = get_cache_key(tenant_id)
        ttl = ttl or settings.cache_ttl_seconds
        await redis_client.setex(key, ttl, json.dumps(data))
    except Exception:
        # Silently fail if Redis is not available (e.g., in tests)
        pass


async def delete_cached_entitlements(tenant_id: str) -> None:
    """Delete cached entitlements for tenant."""
    try:
        redis_client = await get_redis()
        key = get_cache_key(tenant_id)
        await redis_client.delete(key)
    except Exception:
        # Silently fail if Redis is not available (e.g., in tests)
        pass
