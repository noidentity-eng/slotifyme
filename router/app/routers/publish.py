"""Publish router for manifest operations."""

from fastapi import APIRouter, Depends

from app.deps import AdminAuth, InternalAuth
from app.logging import get_logger
from app.schemas.publish import ManifestResponse
from app.services.manifest_service import ManifestService

logger = get_logger(__name__)

router = APIRouter(prefix="/publish", tags=["publish"])


@router.post("", response_model=ManifestResponse)
async def publish_manifest(
    admin_role: str = AdminAuth,
) -> ManifestResponse:
    """Generate and optionally publish manifest."""
    manifest_service = ManifestService()
    
    manifest = await manifest_service.publish_manifest()
    
    logger.info(
        "Manifest published",
        count=manifest.count,
        s3_url=manifest.s3_url,
    )
    
    return manifest


@router.post("/internal", response_model=ManifestResponse)
async def publish_manifest_internal(
    service_name: str = InternalAuth,
) -> ManifestResponse:
    """Generate and optionally publish manifest (internal service access)."""
    manifest_service = ManifestService()
    
    manifest = await manifest_service.publish_manifest()
    
    logger.info(
        "Manifest published (internal)",
        count=manifest.count,
        s3_url=manifest.s3_url,
    )
    
    return manifest
