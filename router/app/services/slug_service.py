"""Slug service with business logic for slug mapping operations."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.cache import invalidate_resolve_cache
from app.logging import get_logger
from app.models.slug_map import SlugMap, SlugStatus
from app.models.slug_history import SlugHistory
from app.schemas.slug import SlugMapCreate, SlugMapUpdate
from app.services.tenant_client import TenantClient

logger = get_logger(__name__)


class SlugService:
    """Service for slug mapping operations."""
    
    def __init__(self, db: AsyncSession, tenant_client: Optional[TenantClient] = None):
        self.db = db
        self.tenant_client = tenant_client
    
    def _generate_id(self) -> str:
        """Generate a unique slug ID."""
        return f"slug_{uuid.uuid4().hex[:12]}"
    
    def _generate_history_id(self) -> str:
        """Generate a unique history ID."""
        return f"hist_{uuid.uuid4().hex[:12]}"
    
    async def _check_conflict(
        self, 
        host: str, 
        path: str, 
        status: SlugStatus = SlugStatus.ACTIVE,
        exclude_id: Optional[str] = None
    ) -> Optional[SlugMap]:
        """Check for conflicting slug mappings."""
        query = select(SlugMap).where(
            and_(
                SlugMap.host == host,
                SlugMap.path == path,
                SlugMap.status == status
            )
        )
        
        if exclude_id:
            query = query.where(SlugMap.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _validate_tenant_resource(
        self, 
        resource_type: str, 
        resource_id: str, 
        tenant_id: Optional[str]
    ) -> None:
        """Validate tenant/location existence if tenant client is configured."""
        if not self.tenant_client:
            return
        
        try:
            if resource_type == "tenant":
                exists = await self.tenant_client.tenant_exists(resource_id)
                if not exists:
                    logger.warning(f"Tenant {resource_id} does not exist")
            elif resource_type == "location":
                exists = await self.tenant_client.location_exists(resource_id)
                if not exists:
                    logger.warning(f"Location {resource_id} does not exist")
        except Exception as e:
            logger.warning(f"Tenant validation failed: {e}")
    
    async def _write_history(
        self, 
        slug_map: SlugMap, 
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        actor: Optional[str] = None
    ) -> None:
        """Write history record for slug mapping changes."""
        history = SlugHistory(
            id=self._generate_history_id(),
            slug_map_id=slug_map.id,
            old_values_json=old_values,
            new_values_json=new_values,
            actor=actor
        )
        self.db.add(history)
        await self.db.flush()
    
    async def create_slug(
        self, 
        slug_data: SlugMapCreate, 
        actor: Optional[str] = None
    ) -> SlugMap:
        """Create a new slug mapping."""
        # Check for conflicts
        conflict = await self._check_conflict(
            slug_data.host, 
            slug_data.path, 
            slug_data.status
        )
        
        if conflict:
            logger.warning(
                "Slug conflict detected",
                host=slug_data.host,
                path=slug_data.path,
                conflicting_id=conflict.id
            )
            raise ValueError(f"SLUG_CONFLICT: Active mapping exists with ID {conflict.id}")
        
        # Validate tenant resource if configured
        await self._validate_tenant_resource(
            slug_data.resource_type,
            slug_data.resource_id,
            slug_data.tenant_id
        )
        
        # Create slug mapping
        slug_map = SlugMap(
            id=self._generate_id(),
            host=slug_data.host,
            path=slug_data.path,
            resource_type=slug_data.resource_type,
            resource_id=slug_data.resource_id,
            tenant_id=slug_data.tenant_id,
            canonical_url=slug_data.canonical_url,
            status=slug_data.status,
            version=1
        )
        
        self.db.add(slug_map)
        await self.db.flush()
        
        # Write history
        await self._write_history(
            slug_map,
            new_values=slug_data.model_dump(),
            actor=actor
        )
        
        await self.db.commit()
        
        logger.info(
            "Slug mapping created",
            slug_id=slug_map.id,
            host=slug_map.host,
            path=slug_map.path
        )
        
        return slug_map
    
    async def update_slug(
        self, 
        slug_id: str, 
        update_data: SlugMapUpdate,
        actor: Optional[str] = None
    ) -> Optional[SlugMap]:
        """Update an existing slug mapping."""
        # Get existing slug
        query = select(SlugMap).where(SlugMap.id == slug_id)
        result = await self.db.execute(query)
        slug_map = result.scalar_one_or_none()
        
        if not slug_map:
            return None
        
        # Store old values for history
        old_values = {
            "host": slug_map.host,
            "path": slug_map.path,
            "resource_type": slug_map.resource_type,
            "resource_id": slug_map.resource_id,
            "tenant_id": slug_map.tenant_id,
            "canonical_url": slug_map.canonical_url,
            "status": slug_map.status,
            "version": slug_map.version
        }
        
        # Check for conflicts if host/path is being changed
        if (update_data.host and update_data.host != slug_map.host) or \
           (update_data.path and update_data.path != slug_map.path):
            
            new_host = update_data.host or slug_map.host
            new_path = update_data.path or slug_map.path
            new_status = update_data.status or slug_map.status
            
            conflict = await self._check_conflict(
                new_host, 
                new_path, 
                new_status,
                exclude_id=slug_id
            )
            
            if conflict:
                logger.warning(
                    "Slug conflict detected during update",
                    host=new_host,
                    path=new_path,
                    conflicting_id=conflict.id
                )
                raise ValueError(f"SLUG_CONFLICT: Active mapping exists with ID {conflict.id}")
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Check if version should be incremented
        version_bump_fields = {"host", "path", "resource_type", "resource_id", "status"}
        should_bump_version = any(field in update_dict for field in version_bump_fields)
        
        if should_bump_version:
            slug_map.version += 1
            # Invalidate cache for old host/path
            await invalidate_resolve_cache(slug_map.host, slug_map.path)
        
        # Apply updates
        for field, value in update_dict.items():
            setattr(slug_map, field, value)
        
        slug_map.updated_at = datetime.utcnow()
        
        # Validate tenant resource if resource is being changed
        if "resource_type" in update_dict or "resource_id" in update_dict:
            await self._validate_tenant_resource(
                slug_map.resource_type,
                slug_map.resource_id,
                slug_map.tenant_id
            )
        
        # Write history
        await self._write_history(
            slug_map,
            old_values=old_values,
            new_values=slug_map.__dict__,
            actor=actor
        )
        
        await self.db.commit()
        
        logger.info(
            "Slug mapping updated",
            slug_id=slug_map.id,
            version=slug_map.version
        )
        
        return slug_map
    
    async def delete_slug(
        self, 
        slug_id: str, 
        soft: bool = True,
        actor: Optional[str] = None
    ) -> Optional[SlugMap]:
        """Delete a slug mapping (soft or hard delete)."""
        query = select(SlugMap).where(SlugMap.id == slug_id)
        result = await self.db.execute(query)
        slug_map = result.scalar_one_or_none()
        
        if not slug_map:
            return None
        
        if soft:
            # Soft delete
            old_values = {
                "host": slug_map.host,
                "path": slug_map.path,
                "resource_type": slug_map.resource_type,
                "resource_id": slug_map.resource_id,
                "tenant_id": slug_map.tenant_id,
                "canonical_url": slug_map.canonical_url,
                "status": slug_map.status,
                "version": slug_map.version
            }
            
            slug_map.status = SlugStatus.DELETED
            slug_map.version += 1
            slug_map.updated_at = datetime.utcnow()
            
            # Write history
            await self._write_history(
                slug_map,
                old_values=old_values,
                new_values=slug_map.__dict__,
                actor=actor
            )
            
            # Invalidate cache
            await invalidate_resolve_cache(slug_map.host, slug_map.path)
            
            await self.db.commit()
            
            logger.info(
                "Slug mapping soft deleted",
                slug_id=slug_map.id
            )
            
            return slug_map
        else:
            # Hard delete
            await invalidate_resolve_cache(slug_map.host, slug_map.path)
            await self.db.delete(slug_map)
            await self.db.commit()
            
            logger.info(
                "Slug mapping hard deleted",
                slug_id=slug_id
            )
            
            return None
    
    async def get_slug(self, slug_id: str) -> Optional[SlugMap]:
        """Get a slug mapping by ID."""
        query = select(SlugMap).where(SlugMap.id == slug_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def resolve_slug(self, host: str, path: str) -> Optional[SlugMap]:
        """Resolve a slug mapping by host and path."""
        query = select(SlugMap).where(
            and_(
                SlugMap.host == host,
                SlugMap.path == path,
                SlugMap.status == SlugStatus.ACTIVE
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_slugs(
        self,
        host: Optional[str] = None,
        tenant_id: Optional[str] = None,
        status: Optional[SlugStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[list[SlugMap], int]:
        """List slug mappings with pagination."""
        # Build query
        query = select(SlugMap)
        count_query = select(SlugMap.id)
        
        conditions = []
        if host:
            conditions.append(SlugMap.host == host)
        if tenant_id:
            conditions.append(SlugMap.tenant_id == tenant_id)
        if status:
            conditions.append(SlugMap.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get total count
        count_result = await self.db.execute(count_query)
        total = len(count_result.scalars().all())
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.order_by(SlugMap.created_at.desc())
        
        # Execute query
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
