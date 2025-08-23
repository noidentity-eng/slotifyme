"""Service for generating and publishing manifest files."""

import json
from datetime import datetime
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from sqlalchemy import select

from app.config import settings
from app.db import AsyncSessionLocal
from app.logging import get_logger
from app.models.slug_map import SlugMap, SlugStatus
from app.schemas.publish import ManifestItem, ManifestResponse

logger = get_logger(__name__)


class ManifestService:
    """Service for manifest generation and publishing."""
    
    def __init__(self):
        self.s3_client = None
        if settings.publish_s3_bucket:
            self.s3_client = boto3.client("s3")
    
    async def build_manifest(self) -> ManifestResponse:
        """Build a compact manifest of all active slug mappings."""
        async with AsyncSessionLocal() as db:
            # Query all active slugs
            query = select(SlugMap).where(SlugMap.status == SlugStatus.ACTIVE)
            result = await db.execute(query)
            slug_maps = result.scalars().all()
            
            # Convert to compact format
            items = []
            for slug_map in slug_maps:
                manifest_item = ManifestItem(
                    host=slug_map.host,
                    path=slug_map.path,
                    resource_type=slug_map.resource_type.value,
                    resource_id=slug_map.resource_id,
                    version=slug_map.version
                )
                items.append(manifest_item.to_compact_format())
            
            # Sort for consistent output
            items.sort(key=lambda x: (x[0], x[1]))
            
            manifest = ManifestResponse(
                generated_at=datetime.utcnow(),
                count=len(items),
                items=items
            )
            
            logger.info(
                "Manifest built",
                count=manifest.count,
                generated_at=manifest.generated_at.isoformat()
            )
            
            return manifest
    
    async def upload_to_s3(self, manifest: ManifestResponse) -> tuple[Optional[str], Optional[str]]:
        """Upload manifest to S3 if configured."""
        if not self.s3_client or not settings.publish_s3_bucket:
            return None, None
        
        try:
            # Convert to JSON
            manifest_json = manifest.model_dump_json()
            
            # Upload to S3
            response = self.s3_client.put_object(
                Bucket=settings.publish_s3_bucket,
                Key="router/manifest.json",
                Body=manifest_json,
                ContentType="application/json",
                CacheControl="max-age=600",  # 10 minutes
                Metadata={
                    "generated_at": manifest.generated_at.isoformat(),
                    "count": str(manifest.count)
                }
            )
            
            s3_url = f"https://{settings.publish_s3_bucket}.s3.amazonaws.com/router/manifest.json"
            etag = response.get("ETag", "").strip('"')
            
            logger.info(
                "Manifest uploaded to S3",
                s3_url=s3_url,
                etag=etag
            )
            
            return s3_url, etag
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            return None, None
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {e}")
            return None, None
    
    async def publish_manifest(self) -> ManifestResponse:
        """Build and optionally upload manifest."""
        # Build manifest
        manifest = await self.build_manifest()
        
        # Upload to S3 if configured
        s3_url, etag = await self.upload_to_s3(manifest)
        
        # Update response with S3 info
        manifest.s3_url = s3_url
        manifest.etag = etag
        
        return manifest
