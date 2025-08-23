"""Stats router for internal statistics endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from tenant.app.db import get_db
from tenant.app.deps import RequireInternal, RequestID
from tenant.app.services.link_service import LinkService
from tenant.app.schemas.link import TenantStatsResponse
from tenant.app.schemas.common import ErrorResponse
from tenant.app.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/internal", tags=["internal"])


@router.get(
    "/tenants/{tenant_id}/stats",
    response_model=TenantStatsResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_tenant_stats(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    request_id: str = RequestID,
    _: None = RequireInternal
):
    """Get statistics for a tenant (internal endpoint)."""
    service = LinkService(db)
    stats = await service.get_tenant_stats(tenant_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "TENANT_NOT_FOUND", "message": f"Tenant {tenant_id} not found"}
        )
    
    response = TenantStatsResponse(**stats)
    
    logger.info("Retrieved tenant stats", tenant_id=tenant_id, request_id=request_id)
    return response
