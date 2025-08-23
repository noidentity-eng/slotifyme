"""Dependency injection utilities."""

from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.logging import get_logger

logger = get_logger(__name__)


async def require_admin(
    x_internal_role: Optional[str] = Header(None, alias="X-Internal-Role")
) -> str:
    """Require admin role for protected endpoints."""
    if x_internal_role != "admin":
        logger.warning("Unauthorized admin access attempt", role=x_internal_role)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return x_internal_role


async def require_internal(
    x_internal_service: Optional[str] = Header(None, alias="X-Internal-Service")
) -> str:
    """Require internal service authentication."""
    if not x_internal_service:
        logger.warning("Missing internal service header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Internal service authentication required",
        )
    return x_internal_service


async def get_idempotency_key(
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
) -> Optional[str]:
    """Get idempotency key from header."""
    return idempotency_key


# Common dependencies
DatabaseSession = Depends(get_db)
AdminAuth = Depends(require_admin)
InternalAuth = Depends(require_internal)
IdempotencyKey = Depends(get_idempotency_key)
