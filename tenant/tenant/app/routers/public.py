"""Public router for public-facing endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from tenant.app.db import get_db
from tenant.app.deps import RequireInternal, RequestID
from tenant.app.services.tenant_service import TenantService
from tenant.app.services.location_service import LocationService
from tenant.app.schemas.tenant import PublicTenantResponse
from tenant.app.schemas.location import PublicLocationResponse, PublicLocationListResponse
from tenant.app.schemas.common import ErrorResponse
from tenant.app.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/public", tags=["public"])


@router.get(
    "/tenants/{slug}",
    response_model=PublicTenantResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_public_tenant(
    slug: str,
    db: AsyncSession = Depends(get_db),
    request_id: str = RequestID,
    _: None = RequireInternal
):
    """Get public tenant information by slug."""
    service = TenantService(db)
    tenant = await service.get_tenant_by_slug(slug)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "TENANT_NOT_FOUND", "message": f"Tenant {slug} not found"}
        )
    
    response = PublicTenantResponse(
        id=tenant.id,
        slug=tenant.slug,
        name=tenant.name,
        theme=tenant.theme_json
    )
    
    logger.info("Retrieved public tenant", slug=slug, request_id=request_id)
    return response


@router.get(
    "/tenants/{tenant_slug}/locations",
    response_model=PublicLocationListResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_public_locations(
    tenant_slug: str,
    db: AsyncSession = Depends(get_db),
    request_id: str = RequestID,
    _: None = RequireInternal
):
    """Get public locations for a tenant."""
    # Get tenant
    tenant_service = TenantService(db)
    tenant = await tenant_service.get_tenant_by_slug(tenant_slug)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "TENANT_NOT_FOUND", "message": f"Tenant {tenant_slug} not found"}
        )
    
    # Get locations
    location_service = LocationService(db)
    locations = await location_service.list_locations(tenant.id)
    
    # Convert to public response models
    public_locations = []
    for location in locations:
        public_location = PublicLocationResponse(
            id=location.id,
            tenant_slug=tenant_slug,
            location_slug=location.slug,
            name=location.name,
            timezone=location.timezone,
            phone_public=location.phone_public,
            phone=location.phone if location.phone_public else None,
            status=location.status
        )
        public_locations.append(public_location)
    
    response = PublicLocationListResponse(
        tenant_slug=tenant_slug,
        locations=public_locations
    )
    
    logger.info("Retrieved public locations", tenant_slug=tenant_slug, count=len(locations), request_id=request_id)
    return response


@router.get(
    "/tenants/{tenant_slug}/locations/{location_slug}",
    response_model=PublicLocationResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_public_location(
    tenant_slug: str,
    location_slug: str,
    db: AsyncSession = Depends(get_db),
    request_id: str = RequestID,
    _: None = RequireInternal
):
    """Get public location information by tenant and location slugs."""
    # Get tenant
    tenant_service = TenantService(db)
    tenant = await tenant_service.get_tenant_by_slug(tenant_slug)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "TENANT_NOT_FOUND", "message": f"Tenant {tenant_slug} not found"}
        )
    
    # Get location
    location_service = LocationService(db)
    location = await location_service.get_location_by_slug(tenant.id, location_slug)
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "LOCATION_NOT_FOUND", "message": f"Location {location_slug} not found"}
        )
    
    response = PublicLocationResponse(
        id=location.id,
        tenant_slug=tenant_slug,
        location_slug=location.slug,
        name=location.name,
        timezone=location.timezone,
        phone_public=location.phone_public,
        phone=location.phone if location.phone_public else None,
        status=location.status
    )
    
    logger.info("Retrieved public location", tenant_slug=tenant_slug, location_slug=location_slug, request_id=request_id)
    return response
