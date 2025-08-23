"""Entitlements router for computing and caching entitlements."""

import json
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_internal_service
from app.services.entitlement_service import EntitlementService
from app.services.cache_service import CacheService
from app.schemas.entitlements import EntitlementsResponse

router = APIRouter(prefix="/entitlements", tags=["entitlements"])


def serialize_datetime(obj):
    """Serialize datetime objects to ISO format strings."""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return obj


@router.get("/{tenant_id}", response_model=EntitlementsResponse)
async def get_entitlements(
    tenant_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(require_internal_service),
):
    """Get computed entitlements for a tenant."""
    cache_service = CacheService()
    
    # Try to get from cache first
    cached_data = await cache_service.get_entitlements(tenant_id)
    if cached_data:
        # Calculate ETag for cached data
        etag = cache_service.calculate_etag(cached_data)
        return Response(
            content=json.dumps(cached_data, default=serialize_datetime),
            media_type="application/json",
            headers={"ETag": etag}
        )
    
    # Compute entitlements
    try:
        entitlement_service = EntitlementService(db)
        entitlements = entitlement_service.compute_entitlements(tenant_id)
        
        # Convert to dict for caching
        entitlements_dict = entitlements.model_dump()
        
        # Cache the result
        await cache_service.set_entitlements(tenant_id, entitlements_dict)
        
        # Calculate ETag
        etag = cache_service.calculate_etag(entitlements_dict)
        
        return Response(
            content=json.dumps(entitlements_dict, default=serialize_datetime),
            media_type="application/json",
            headers={"ETag": etag}
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
