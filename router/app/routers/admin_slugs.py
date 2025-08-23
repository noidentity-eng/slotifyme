"""Admin router for slug mapping operations."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import AdminAuth, DatabaseSession, IdempotencyKey
from app.logging import get_logger
from app.models.slug_map import SlugStatus
from app.schemas.slug import (
    SlugAvailabilityResponse,
    SlugMapCreate,
    SlugMapListResponse,
    SlugMapResponse,
    SlugMapUpdate,
)
from app.services.idempotency import IdempotencyService
from app.services.slug_service import SlugService
from app.services.tenant_client import get_tenant_client

logger = get_logger(__name__)

router = APIRouter(prefix="/admin/slugs", tags=["admin"])


@router.post("", response_model=SlugMapResponse, status_code=status.HTTP_201_CREATED)
async def create_slug(
    slug_data: SlugMapCreate,
    db: DatabaseSession,
    admin_role: str = AdminAuth,
    idempotency_key: Optional[str] = IdempotencyKey,
) -> SlugMapResponse:
    """Create a new slug mapping."""
    # Check idempotency
    if idempotency_key:
        cached_result = await IdempotencyService.check_idempotency(
            idempotency_key, "create_slug", slug_data.model_dump()
        )
        if cached_result:
            # Return cached result (would need to deserialize properly in production)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Operation already performed",
            )
    
    # Initialize services
    tenant_client = get_tenant_client()
    slug_service = SlugService(db, tenant_client)
    
    try:
        slug_map = await slug_service.create_slug(slug_data, actor=admin_role)
        
        # Store idempotency result
        if idempotency_key:
            await IdempotencyService.store_idempotency_result(
                idempotency_key,
                "create_slug",
                slug_data.model_dump(),
                slug_map.id,
            )
        
        return SlugMapResponse.model_validate(slug_map)
        
    except ValueError as e:
        if "SLUG_CONFLICT" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{slug_id}", response_model=SlugMapResponse)
async def update_slug(
    slug_id: str,
    update_data: SlugMapUpdate,
    db: DatabaseSession,
    admin_role: str = AdminAuth,
) -> SlugMapResponse:
    """Update an existing slug mapping."""
    tenant_client = get_tenant_client()
    slug_service = SlugService(db, tenant_client)
    
    slug_map = await slug_service.update_slug(slug_id, update_data, actor=admin_role)
    
    if not slug_map:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slug mapping not found",
        )
    
    return SlugMapResponse.model_validate(slug_map)


@router.delete("/{slug_id}", response_model=SlugMapResponse)
async def delete_slug(
    slug_id: str,
    soft: bool = Query(True, description="Whether to soft delete"),
    db: DatabaseSession = Depends(get_db),
    admin_role: str = AdminAuth,
) -> SlugMapResponse:
    """Delete a slug mapping."""
    tenant_client = get_tenant_client()
    slug_service = SlugService(db, tenant_client)
    
    slug_map = await slug_service.delete_slug(slug_id, soft=soft, actor=admin_role)
    
    if not slug_map:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slug mapping not found",
        )
    
    return SlugMapResponse.model_validate(slug_map)


@router.get("", response_model=SlugMapListResponse)
async def list_slugs(
    host: Optional[str] = Query(None, description="Filter by host"),
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    status: Optional[SlugStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: DatabaseSession = Depends(get_db),
    admin_role: str = AdminAuth,
) -> SlugMapListResponse:
    """List slug mappings with pagination."""
    tenant_client = get_tenant_client()
    slug_service = SlugService(db, tenant_client)
    
    items, total = await slug_service.list_slugs(
        host=host,
        tenant_id=tenant_id,
        status=status,
        page=page,
        page_size=page_size,
    )
    
    pages = (total + page_size - 1) // page_size
    
    return SlugMapListResponse(
        items=[SlugMapResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{slug_id}", response_model=SlugMapResponse)
async def get_slug(
    slug_id: str,
    db: DatabaseSession = Depends(get_db),
    admin_role: str = AdminAuth,
) -> SlugMapResponse:
    """Get a slug mapping by ID."""
    tenant_client = get_tenant_client()
    slug_service = SlugService(db, tenant_client)
    
    slug_map = await slug_service.get_slug(slug_id)
    
    if not slug_map:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slug mapping not found",
        )
    
    return SlugMapResponse.model_validate(slug_map)


@router.get("/check-availability", response_model=SlugAvailabilityResponse)
async def check_availability(
    host: str = Query(..., description="Host to check"),
    path: str = Query(..., description="Path to check"),
    db: DatabaseSession = Depends(get_db),
    admin_role: str = AdminAuth,
) -> SlugAvailabilityResponse:
    """Check if a slug is available."""
    tenant_client = get_tenant_client()
    slug_service = SlugService(db, tenant_client)
    
    conflict = await slug_service._check_conflict(host, path, SlugStatus.ACTIVE)
    
    return SlugAvailabilityResponse(
        available=conflict is None,
        conflicting_id=conflict.id if conflict else None,
    )
