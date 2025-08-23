"""Dependencies for authentication and authorization."""

from fastapi import Depends, HTTPException, Header
from typing import Optional

from app.config import settings


async def require_admin(
    x_internal_role: Optional[str] = Header(None, alias=settings.admin_role_header)
) -> str:
    """Require admin role header."""
    if not x_internal_role or x_internal_role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )
    return x_internal_role


async def require_internal_service(
    x_internal_service: Optional[str] = Header(None, alias=settings.internal_service_header)
) -> str:
    """Require internal service header."""
    if not x_internal_service:
        raise HTTPException(
            status_code=403,
            detail="Internal service access required",
        )
    return x_internal_service
