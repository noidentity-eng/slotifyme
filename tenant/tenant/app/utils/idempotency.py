"""Idempotency utilities for handling duplicate requests."""

import hashlib
import json
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import redis.asyncio as redis
from tenant.app.config import settings
from tenant.app.logging import get_logger

logger = get_logger(__name__)


class IdempotencyService:
    """Service for handling idempotent requests."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.ttl_hours = settings.idempotency_ttl_hours
    
    async def _get_redis(self) -> redis.Redis:
        """Get Redis client, creating it if needed."""
        if self.redis_client is None:
            self.redis_client = redis.from_url(settings.redis_url)
        return self.redis_client
    
    async def _generate_request_hash(self, method: str, path: str, body: Dict[str, Any]) -> str:
        """Generate a hash of the request for deduplication."""
        request_data = {
            "method": method,
            "path": path,
            "body": body
        }
        request_json = json.dumps(request_data, sort_keys=True)
        return hashlib.sha256(request_json.encode()).hexdigest()
    
    async def check_idempotency(
        self, 
        idempotency_key: str, 
        method: str, 
        path: str, 
        body: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Check if this is a duplicate request and return cached response if so."""
        try:
            redis_client = await self._get_redis()
            
            # Generate request hash
            request_hash = await self._generate_request_hash(method, path, body)
            
            # Check if we have a cached response
            cache_key = f"idempotency:{idempotency_key}"
            cached_data = await redis_client.get(cache_key)
            
            if cached_data:
                cached = json.loads(cached_data)
                
                # Verify the request hash matches (same request)
                if cached.get("request_hash") == request_hash:
                    logger.info("Idempotency hit", idempotency_key=idempotency_key)
                    return cached.get("response")
                else:
                    logger.warning("Idempotency key conflict", idempotency_key=idempotency_key)
                    return None
            
            return None
            
        except Exception as e:
            logger.error("Error checking idempotency", error=str(e))
            return None
    
    async def store_response(
        self, 
        idempotency_key: str, 
        method: str, 
        path: str, 
        body: Dict[str, Any], 
        response: Dict[str, Any]
    ) -> None:
        """Store the response for future idempotency checks."""
        try:
            redis_client = await self._get_redis()
            
            # Generate request hash
            request_hash = await self._generate_request_hash(method, path, body)
            
            # Store response with TTL
            cache_data = {
                "request_hash": request_hash,
                "response": response,
                "created_at": datetime.utcnow().isoformat()
            }
            
            cache_key = f"idempotency:{idempotency_key}"
            ttl_seconds = self.ttl_hours * 3600
            
            await redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(cache_data)
            )
            
            logger.info("Stored idempotency response", idempotency_key=idempotency_key)
            
        except Exception as e:
            logger.error("Error storing idempotency response", error=str(e))
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()


# Global idempotency service instance
idempotency_service = IdempotencyService()
