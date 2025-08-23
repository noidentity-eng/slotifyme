"""Resolve router for URL resolution operations."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.cache import get_cached_resolve, set_cached_resolve
from app.deps import DatabaseSession, InternalAuth
from app.db import get_db
from app.models.slug_map import SlugStatus
from app.logging import get_logger
from app.schemas.resolve import CacheInfo, ResourceInfo, ResolveResponse
from app.services.slug_service import SlugService
from app.services.tenant_client import get_tenant_client

logger = get_logger(__name__)

router = APIRouter(prefix="/resolve", tags=["resolve"])


@router.get("", response_model=ResolveResponse)
async def resolve_url(
    host: str = Query(..., description="Host to resolve"),
    path: str = Query(..., description="Path to resolve"),
    db: DatabaseSession = Depends(get_db),
    service_name: str = InternalAuth,
) -> ResolveResponse:
    """Resolve a URL to its corresponding resource."""
    # Check cache first
    cached_result = await get_cached_resolve(host, path)
    if cached_result:
        logger.debug("Cache hit for resolve", host=host, path=path)
        return ResolveResponse(**cached_result)
    
    # Initialize services
    tenant_client = get_tenant_client()
    slug_service = SlugService(db, tenant_client)
    
    # Resolve from database
    slug_map = await slug_service.resolve_slug(host, path)
    
    if not slug_map:
        # Check if there's a deleted mapping
        deleted_mapping = await slug_service._check_conflict(host, path, SlugStatus.DELETED)
        if deleted_mapping:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Slug mapping has been deleted",
            )
        
        # No mapping found
        return ResolveResponse(match=False)
    
    # Build response
    resource = ResourceInfo(
        type=slug_map.resource_type,
        id=slug_map.resource_id,
    )
    
    cache_info = CacheInfo(
        max_age=600,  # 10 minutes
        etag=f'W/"{slug_map.resource_id}-v{slug_map.version}"',
    )
    
    response = ResolveResponse(
        match=True,
        resource=resource,
        tenant_id=slug_map.tenant_id,
        version=slug_map.version,
        canonical_url=slug_map.canonical_url,
        cache=cache_info,
    )
    
    # Cache the result
    await set_cached_resolve(host, path, response.model_dump())
    
    logger.info(
        "URL resolved",
        host=host,
        path=path,
        resource_type=slug_map.resource_type.value,
        resource_id=slug_map.resource_id,
    )
    
    return response
