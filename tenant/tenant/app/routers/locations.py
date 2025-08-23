"""Locations router for superadmin endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from tenant.app.db import get_db
from tenant.app.deps import RequireAdmin, RequestID
from tenant.app.services.location_service import LocationService
from tenant.app.services.rules_client import rules_client
from tenant.app.schemas.location import (
    LocationCreate, LocationUpdate, LocationResponse, LocationCreateResponse,
    LocationListResponse
)
from tenant.app.schemas.common import ErrorResponse
from tenant.app.utils.idempotency import idempotency_service
from tenant.app.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/tenants/{tenant_id}/locations", tags=["locations"])


@router.post(
    "",
    response_model=LocationCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse}
    }
)
async def create_location(
    tenant_id: str,
    location_data: LocationCreate,
    db: AsyncSession = Depends(get_db),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    request_id: str = RequestID,
    _: None = RequireAdmin
):
    """Create a new location for a tenant (idempotent)."""
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "IDEMPOTENCY_KEY_REQUIRED", "message": "Idempotency-Key header is required"}
        )
    
    # Check idempotency
    cached_response = await idempotency_service.check_idempotency(
        idempotency_key, "POST", f"/tenants/{tenant_id}/locations", location_data.dict()
    )
    if cached_response:
        return LocationCreateResponse(**cached_response)
    
    try:
        service = LocationService(db)
        
        # Check location limit (optional rules check)
        current_locations = await service.list_locations(tenant_id)
        if not await rules_client.check_location_limit(tenant_id, len(current_locations)):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"error_code": "RULES_LIMIT_EXCEEDED", "message": "Location limit exceeded"}
            )
        
        location = await service.create_location(tenant_id, location_data)
        
        response = LocationCreateResponse(
            location_id=location.id,
            slug=location.slug
        )
        
        # Store for idempotency
        await idempotency_service.store_response(
            idempotency_key, "POST", f"/tenants/{tenant_id}/locations", location_data.dict(), response.dict()
        )
        
        logger.info("Created location", tenant_id=tenant_id, location_id=location.id, request_id=request_id)
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error_code": "INVALID_LOCATION_DATA", "message": str(e)}
        )


@router.get(
    "",
    response_model=list[LocationListResponse]
)
async def list_locations(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    request_id: str = RequestID,
    _: None = RequireAdmin
):
    """List all locations for a tenant."""
    service = LocationService(db)
    locations = await service.list_locations(tenant_id)
    
    # Convert to response models
    location_responses = [
        LocationListResponse(
            location_id=location.id,
            slug=location.slug,
            name=location.name,
            timezone=location.timezone,
            phone_public=location.phone_public,
            status=location.status
        ) for location in locations
    ]
    
    logger.info("Listed locations", tenant_id=tenant_id, count=len(locations), request_id=request_id)
    return location_responses


@router.get(
    "/{location_id}",
    response_model=LocationResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_location(
    tenant_id: str,
    location_id: str,
    db: AsyncSession = Depends(get_db),
    request_id: str = RequestID,
    _: None = RequireAdmin
):
    """Get a location by ID."""
    service = LocationService(db)
    location = await service.get_location(location_id)
    
    if not location or location.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "LOCATION_NOT_FOUND", "message": f"Location {location_id} not found"}
        )
    
    response = LocationResponse(
        location_id=location.id,
        tenant_id=location.tenant_id,
        slug=location.slug,
        name=location.name,
        address=location.address_json,
        timezone=location.timezone,
        phone=location.phone,
        phone_public=location.phone_public,
        status=location.status,
        created_at=location.created_at,
        updated_at=location.updated_at
    )
    
    logger.info("Retrieved location", tenant_id=tenant_id, location_id=location_id, request_id=request_id)
    return response


@router.put(
    "/{location_id}",
    response_model=LocationResponse,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse}
    }
)
async def update_location(
    tenant_id: str,
    location_id: str,
    location_data: LocationUpdate,
    db: AsyncSession = Depends(get_db),
    request_id: str = RequestID,
    _: None = RequireAdmin
):
    """Update a location."""
    service = LocationService(db)
    location = await service.get_location(location_id)
    
    if not location or location.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "LOCATION_NOT_FOUND", "message": f"Location {location_id} not found"}
        )
    
    try:
        updated_location = await service.update_location(location_id, location_data)
        
        response = LocationResponse(
            location_id=updated_location.id,
            tenant_id=updated_location.tenant_id,
            slug=updated_location.slug,
            name=updated_location.name,
            address=updated_location.address_json,
            timezone=updated_location.timezone,
            phone=updated_location.phone,
            phone_public=updated_location.phone_public,
            status=updated_location.status,
            created_at=updated_location.created_at,
            updated_at=updated_location.updated_at
        )
        
        logger.info("Updated location", tenant_id=tenant_id, location_id=location_id, request_id=request_id)
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error_code": "INVALID_LOCATION_DATA", "message": str(e)}
        )
