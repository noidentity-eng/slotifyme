"""Links router for user-tenant relationships."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from tenant.app.db import get_db
from tenant.app.deps import RequireAdmin, RequestID
from tenant.app.services.link_service import LinkService
from tenant.app.schemas.link import (
    UserLinkCreate, UserLinkResponse, UserLinkListResponse, UserLinkQuery,
    LinkResponse, TenantStatsResponse
)
from tenant.app.schemas.common import ErrorResponse
from tenant.app.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/tenants/{tenant_id}/users", tags=["links"])


@router.post(
    "",
    response_model=LinkResponse
)
async def link_user(
    tenant_id: str,
    user_data: UserLinkCreate,
    db: AsyncSession = Depends(get_db),
    request_id: str = RequestID,
    _: None = RequireAdmin
):
    """Link a user to a tenant with a specific role."""
    try:
        service = LinkService(db)
        user_link = await service.link_user(tenant_id, user_data)
        
        response = LinkResponse(
            linked=True,
            message=f"User {user_data.user_id} linked to tenant {tenant_id} as {user_data.role}"
        )
        
        logger.info("Linked user", tenant_id=tenant_id, user_id=user_data.user_id, role=user_data.role, request_id=request_id)
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "TENANT_NOT_FOUND", "message": str(e)}
        )


@router.delete(
    "/{user_id}",
    response_model=LinkResponse
)
async def unlink_user(
    tenant_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    request_id: str = RequestID,
    _: None = RequireAdmin
):
    """Unlink a user from a tenant."""
    service = LinkService(db)
    success = await service.unlink_user(tenant_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "USER_LINK_NOT_FOUND", "message": f"User {user_id} not linked to tenant {tenant_id}"}
        )
    
    response = LinkResponse(
        linked=False,
        message=f"User {user_id} unlinked from tenant {tenant_id}"
    )
    
    logger.info("Unlinked user", tenant_id=tenant_id, user_id=user_id, request_id=request_id)
    return response


@router.get(
    "",
    response_model=list[UserLinkListResponse]
)
async def list_users(
    tenant_id: str,
    role: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    request_id: str = RequestID,
    _: None = RequireAdmin
):
    """List users linked to a tenant."""
    service = LinkService(db)
    
    query = None
    if role:
        query = UserLinkQuery(role=role)
    
    user_links = await service.list_users(tenant_id, query)
    
    # Convert to response models
    user_responses = [
        UserLinkListResponse(
            tenant_id=link.tenant_id,
            user_id=link.user_id,
            role=link.role,
            created_at=link.created_at
        ) for link in user_links
    ]
    
    logger.info("Listed users", tenant_id=tenant_id, count=len(user_links), request_id=request_id)
    return user_responses


@router.get(
    "/stats",
    response_model=TenantStatsResponse
)
async def get_tenant_stats(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    request_id: str = RequestID,
    _: None = RequireAdmin
):
    """Get statistics for a tenant."""
    service = LinkService(db)
    stats = await service.get_tenant_stats(tenant_id)
    
    response = TenantStatsResponse(**stats)
    
    logger.info("Retrieved tenant stats", tenant_id=tenant_id, request_id=request_id)
    return response
