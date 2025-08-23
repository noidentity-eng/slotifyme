"""Idempotency service for handling idempotent operations."""

import hashlib
import json
from typing import Any, Optional

from app.cache import get_idempotency_key, set_idempotency_key
from app.logging import get_logger

logger = get_logger(__name__)


class IdempotencyService:
    """Service for handling idempotent operations."""
    
    @staticmethod
    def generate_key(operation: str, data: dict[str, Any]) -> str:
        """Generate idempotency key from operation and data."""
        # Create a deterministic string representation
        data_str = json.dumps(data, sort_keys=True)
        key_data = f"{operation}:{data_str}"
        
        # Hash to create a fixed-length key
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]
    
    @staticmethod
    async def check_idempotency(
        idempotency_key: Optional[str],
        operation: str,
        data: dict[str, Any]
    ) -> Optional[str]:
        """Check if operation has already been performed."""
        if not idempotency_key:
            return None
        
        # Generate key from operation and data
        generated_key = IdempotencyService.generate_key(operation, data)
        
        # Check cache for existing result
        cached_result = await get_idempotency_key(generated_key)
        if cached_result:
            logger.info(
                "Idempotent operation detected",
                operation=operation,
                key=generated_key
            )
            return cached_result
        
        return None
    
    @staticmethod
    async def store_idempotency_result(
        idempotency_key: Optional[str],
        operation: str,
        data: dict[str, Any],
        result: str,
        ttl: int = 3600
    ) -> None:
        """Store idempotency result for future checks."""
        if not idempotency_key:
            return
        
        # Generate key from operation and data
        generated_key = IdempotencyService.generate_key(operation, data)
        
        # Store result in cache
        await set_idempotency_key(generated_key, result, ttl)
        
        logger.info(
            "Idempotency result stored",
            operation=operation,
            key=generated_key
        )
