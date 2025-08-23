"""Dependency injection functions."""

from typing import Optional
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from tenant.app.db import get_db
from tenant.app.config import settings


async def require_admin(
    x_internal_role: Optional[str] = Header(None, alias="X-Internal-Role")
) -> None:
    """Require admin role for superadmin endpoints."""
    if x_internal_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


async def require_internal(
    x_internal_service: Optional[str] = Header(None, alias="X-Internal-Service")
) -> None:
    """Require internal service header for S2S calls."""
    if not x_internal_service:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Internal service access required"
        )


async def get_request_id(
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID")
) -> str:
    """Get or generate request ID."""
    return x_request_id or "req_" + str(hash(str(id(x_request_id))))


# Database dependency
DB = Depends(get_db)

# Admin dependency
RequireAdmin = Depends(require_admin)

# Internal service dependency
RequireInternal = Depends(require_internal)

# Request ID dependency
RequestID = Depends(get_request_id)
