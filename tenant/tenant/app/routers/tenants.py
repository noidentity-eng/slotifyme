"""Tenants router for superadmin endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from tenant.app.db import get_db
from tenant.app.deps import RequireAdmin, RequestID
from tenant.app.services.tenant_service import TenantService
from tenant.app.schemas.tenant import (
    TenantCreate, TenantUpdate, TenantResponse, TenantCreateResponse,
    TenantListResponse, TenantListQuery
)
from tenant.app.schemas.common import ErrorResponse
from tenant.app.utils.pagination import PaginatedResponse
from tenant.app.utils.idempotency import idempotency_service
from tenant.app.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post(
    "",
    response_model=TenantCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse}
    }
)
async def create_tenant(
    tenant_data: TenantCreate,
    db: AsyncSession = Depends(get_db),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    request_id: str = RequestID,
    _: None = RequireAdmin
):
    """Create a new tenant (idempotent)."""
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "IDEMPOTENCY_KEY_REQUIRED", "message": "Idempotency-Key header is required"}
        )
    
    # Check idempotency
    cached_response = await idempotency_service.check_idempotency(
        idempotency_key, "POST", "/tenants", tenant_data.dict()
    )
    if cached_response:
        return TenantCreateResponse(**cached_response)
    
    try:
        service = TenantService(db)
        tenant = await service.create_tenant(tenant_data)
        
        response = TenantCreateResponse(
            tenant_id=tenant.id,
            name=tenant.name,
            slug=tenant.slug
        )
        
        # Store for idempotency
        await idempotency_service.store_response(
            idempotency_key, "POST", "/tenants", tenant_data.dict(), response.dict()
        )
        
        logger.info("Created tenant", tenant_id=tenant.id, request_id=request_id)
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error_code": "INVALID_SLUG", "message": str(e)}
        )


@router.get(
    "",
    response_model=PaginatedResponse[TenantListResponse]
)
async def list_tenants(
    q: Optional[str] = None,
    status_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    request_id: str = RequestID,
    _: None = RequireAdmin
):
    """List tenants with pagination and filtering."""
    query = TenantListQuery(
        q=q,
        status=status_filter,
        page=page,
        page_size=page_size
    )
    
    service = TenantService(db)
    tenants, total = await service.list_tenants(query)
    
    # Convert to response models
    tenant_responses = [
        TenantListResponse(**tenant) for tenant in tenants
    ]
    
    # Calculate pagination info
    total_pages = (total + page_size - 1) // page_size
    has_next = page < total_pages
    has_prev = page > 1
    
    response = PaginatedResponse(
        items=tenant_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev
    )
    
    logger.info("Listed tenants", count=len(tenants), request_id=request_id)
    return response


@router.get(
    "/{tenant_id}",
    response_model=TenantResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_tenant(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    request_id: str = RequestID,
    _: None = RequireAdmin
):
    """Get a tenant by ID."""
    service = TenantService(db)
    tenant = await service.get_tenant(tenant_id)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "TENANT_NOT_FOUND", "message": f"Tenant {tenant_id} not found"}
        )
    
    response = TenantResponse(
        tenant_id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        status=tenant.status,
        theme=tenant.theme_json,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at
    )
    
    logger.info("Retrieved tenant", tenant_id=tenant_id, request_id=request_id)
    return response


@router.put(
    "/{tenant_id}",
    response_model=TenantResponse,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse}
    }
)
async def update_tenant(
    tenant_id: str,
    tenant_data: TenantUpdate,
    db: AsyncSession = Depends(get_db),
    request_id: str = RequestID,
    _: None = RequireAdmin
):
    """Update a tenant."""
    service = TenantService(db)
    tenant = await service.update_tenant(tenant_id, tenant_data)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "TENANT_NOT_FOUND", "message": f"Tenant {tenant_id} not found"}
        )
    
    response = TenantResponse(
        tenant_id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        status=tenant.status,
        theme=tenant.theme_json,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at
    )
    
    logger.info("Updated tenant", tenant_id=tenant_id, request_id=request_id)
    return response
