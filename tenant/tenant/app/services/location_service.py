"""Location service with business logic."""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from ulid import ULID
from tenant.app.models.location import Location, LocationStatus
from tenant.app.models.tenant import Tenant
from tenant.app.schemas.location import LocationCreate, LocationUpdate
from tenant.app.utils.slug import slugify, is_valid_slug, generate_unique_slug
from tenant.app.logging import get_logger
from tenant.app.services.events import emit_event

logger = get_logger(__name__)


class LocationService:
    """Service for location operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_location(self, tenant_id: str, location_data: LocationCreate) -> Location:
        """Create a new location for a tenant."""
        # Verify tenant exists
        tenant = await self._get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")
        
        # Generate or validate slug
        if location_data.slug:
            if not is_valid_slug(location_data.slug):
                raise ValueError(f"Invalid slug: {location_data.slug}")
            slug = location_data.slug
        else:
            slug = slugify(location_data.name)
        
        # Check slug uniqueness within tenant
        existing_slugs = await self._get_tenant_location_slugs(tenant_id)
        if slug in existing_slugs:
            slug = generate_unique_slug(location_data.name, existing_slugs)
        
        # Create location
        location = Location(
            id=str(ULID()),
            tenant_id=tenant_id,
            slug=slug,
            name=location_data.name,
            address_json=location_data.address.dict() if location_data.address else None,
            timezone=location_data.timezone,
            phone=location_data.phone,
            phone_public=location_data.phone_public,
            status=location_data.status
        )
        
        self.db.add(location)
        await self.db.commit()
        await self.db.refresh(location)
        
        # Emit event
        await emit_event("LocationCreated", {
            "tenant_id": tenant_id,
            "location_id": location.id,
            "name": location.name,
            "slug": location.slug
        })
        
        logger.info("Created location", tenant_id=tenant_id, location_id=location.id, slug=location.slug)
        return location
    
    async def get_location(self, location_id: str) -> Optional[Location]:
        """Get a location by ID."""
        result = await self.db.execute(
            select(Location).where(Location.id == location_id)
        )
        return result.scalar_one_or_none()
    
    async def get_location_by_slug(self, tenant_id: str, slug: str) -> Optional[Location]:
        """Get a location by tenant ID and slug."""
        result = await self.db.execute(
            select(Location).where(
                and_(Location.tenant_id == tenant_id, Location.slug == slug)
            )
        )
        return result.scalar_one_or_none()
    
    async def update_location(self, location_id: str, location_data: LocationUpdate) -> Optional[Location]:
        """Update a location."""
        location = await self.get_location(location_id)
        if not location:
            return None
        
        # Update fields
        if location_data.name is not None:
            location.name = location_data.name
        if location_data.address is not None:
            location.address_json = location_data.address.dict()
        if location_data.timezone is not None:
            location.timezone = location_data.timezone
        if location_data.phone is not None:
            location.phone = location_data.phone
        if location_data.phone_public is not None:
            location.phone_public = location_data.phone_public
        if location_data.status is not None:
            location.status = location_data.status
        
        await self.db.commit()
        await self.db.refresh(location)
        
        # Emit event
        await emit_event("LocationUpdated", {
            "tenant_id": location.tenant_id,
            "location_id": location.id,
            "name": location.name,
            "slug": location.slug
        })
        
        logger.info("Updated location", location_id=location.id)
        return location
    
    async def list_locations(self, tenant_id: str) -> List[Location]:
        """List all locations for a tenant."""
        result = await self.db.execute(
            select(Location)
            .where(Location.tenant_id == tenant_id)
            .order_by(Location.name)
        )
        return result.scalars().all()
    
    async def _get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get a tenant by ID."""
        result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_tenant_location_slugs(self, tenant_id: str) -> List[str]:
        """Get all location slugs for a tenant."""
        result = await self.db.execute(
            select(Location.slug).where(Location.tenant_id == tenant_id)
        )
        return [row[0] for row in result.fetchall()]
