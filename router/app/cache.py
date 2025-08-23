"""Redis cache configuration and utilities."""

import json
from typing import Any, Optional

import redis.asyncio as redis
from app.config import settings
from app.logging import get_logger

logger = get_logger(__name__)

# Redis client
redis_client: Optional[redis.Redis] = None


async def init_cache() -> None:
    """Initialize Redis cache client."""
    global redis_client
    
    if not settings.redis_url:
        logger.info("Redis URL not configured, caching disabled")
        return
    
    try:
        redis_client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_keepalive=True,
        )
        # Test connection
        await redis_client.ping()
        logger.info("Redis cache initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Redis cache: {e}")
        redis_client = None


async def close_cache() -> None:
    """Close Redis cache connection."""
    global redis_client
    
    if redis_client:
        await redis_client.close()
        redis_client = None


def get_cache_key(host: str, path: str) -> str:
    """Generate cache key for resolve operations."""
    return f"router:resolve:{host}|{path}"


async def get_cached_resolve(host: str, path: str) -> Optional[dict[str, Any]]:
    """Get cached resolve result."""
    if not redis_client:
        return None
    
    try:
        key = get_cache_key(host, path)
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        logger.warning(f"Cache get error: {e}")
    
    return None


async def set_cached_resolve(
    host: str, 
    path: str, 
    data: dict[str, Any], 
    ttl: Optional[int] = None
) -> None:
    """Set cached resolve result."""
    if not redis_client:
        return
    
    try:
        key = get_cache_key(host, path)
        ttl = ttl or settings.cache_ttl
        await redis_client.setex(key, ttl, json.dumps(data))
    except Exception as e:
        logger.warning(f"Cache set error: {e}")


async def invalidate_resolve_cache(host: str, path: str) -> None:
    """Invalidate cached resolve result."""
    if not redis_client:
        return
    
    try:
        key = get_cache_key(host, path)
        await redis_client.delete(key)
    except Exception as e:
        logger.warning(f"Cache invalidation error: {e}")


async def get_idempotency_key(key: str) -> Optional[str]:
    """Get idempotency key from cache."""
    if not redis_client:
        return None
    
    try:
        return await redis_client.get(f"router:idempotency:{key}")
    except Exception as e:
        logger.warning(f"Idempotency key get error: {e}")
        return None


async def set_idempotency_key(key: str, value: str, ttl: int = 3600) -> None:
    """Set idempotency key in cache."""
    if not redis_client:
        return
    
    try:
        await redis_client.setex(f"router:idempotency:{key}", ttl, value)
    except Exception as e:
        logger.warning(f"Idempotency key set error: {e}")
