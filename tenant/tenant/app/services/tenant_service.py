"""Tenant service with business logic."""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from ulid import ULID
from tenant.app.models.tenant import Tenant, TenantStatus
from tenant.app.models.location import Location
from tenant.app.models.tenant_user import TenantUser, UserRole
from tenant.app.schemas.tenant import TenantCreate, TenantUpdate, TenantListQuery
from tenant.app.utils.slug import slugify, is_valid_slug, generate_unique_slug
from tenant.app.logging import get_logger
from tenant.app.services.events import emit_event

logger = get_logger(__name__)


class TenantService:
    """Service for tenant operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_tenant(self, tenant_data: TenantCreate) -> Tenant:
        """Create a new tenant."""
        # Generate or validate slug
        if tenant_data.slug:
            if not is_valid_slug(tenant_data.slug):
                raise ValueError(f"Invalid slug: {tenant_data.slug}")
            slug = tenant_data.slug
        else:
            slug = slugify(tenant_data.name)
        
        # Check slug uniqueness
        existing_slugs = await self._get_all_tenant_slugs()
        if slug in existing_slugs:
            slug = generate_unique_slug(tenant_data.name, existing_slugs)
        
        # Create tenant
        tenant = Tenant(
            id=str(ULID()),
            slug=slug,
            name=tenant_data.name,
            theme_json=tenant_data.theme.dict() if tenant_data.theme else None
        )
        
        self.db.add(tenant)
        await self.db.commit()
        await self.db.refresh(tenant)
        
        # Emit event
        await emit_event("TenantCreated", {
            "tenant_id": tenant.id,
            "name": tenant.name,
            "slug": tenant.slug
        })
        
        logger.info("Created tenant", tenant_id=tenant.id, slug=tenant.slug)
        return tenant
    
    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get a tenant by ID."""
        result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        return result.scalar_one_or_none()
    
    async def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get a tenant by slug."""
        result = await self.db.execute(
            select(Tenant).where(Tenant.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def update_tenant(self, tenant_id: str, tenant_data: TenantUpdate) -> Optional[Tenant]:
        """Update a tenant."""
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            return None
        
        # Update fields
        if tenant_data.name is not None:
            tenant.name = tenant_data.name
        if tenant_data.status is not None:
            tenant.status = tenant_data.status
        if tenant_data.theme is not None:
            tenant.theme_json = tenant_data.theme.dict()
        
        await self.db.commit()
        await self.db.refresh(tenant)
        
        logger.info("Updated tenant", tenant_id=tenant.id)
        return tenant
    
    async def list_tenants(self, query: TenantListQuery) -> tuple[List[Dict[str, Any]], int]:
        """List tenants with pagination and filtering."""
        # Build base query
        base_query = select(Tenant)
        
        # Apply filters
        if query.q:
            search_term = f"%{query.q}%"
            base_query = base_query.where(
                (Tenant.name.ilike(search_term)) | (Tenant.slug.ilike(search_term))
            )
        
        if query.status:
            base_query = base_query.where(Tenant.status == query.status)
        
        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self.db.scalar(count_query)
        
        # Apply pagination
        offset = (query.page - 1) * query.page_size
        base_query = base_query.offset(offset).limit(query.page_size)
        
        # Execute query
        result = await self.db.execute(base_query)
        tenants = result.scalars().all()
        
        # Get location counts
        tenant_ids = [t.id for t in tenants]
        location_counts = await self._get_location_counts(tenant_ids)
        
        # Build response
        tenant_list = []
        for tenant in tenants:
            tenant_dict = {
                "tenant_id": tenant.id,
                "name": tenant.name,
                "slug": tenant.slug,
                "status": tenant.status,
                "locations_count": location_counts.get(tenant.id, 0)
            }
            tenant_list.append(tenant_dict)
        
        return tenant_list, total
    
    async def _get_all_tenant_slugs(self) -> List[str]:
        """Get all existing tenant slugs."""
        result = await self.db.execute(select(Tenant.slug))
        return [row[0] for row in result.fetchall()]
    
    async def _get_location_counts(self, tenant_ids: List[str]) -> Dict[str, int]:
        """Get location counts for given tenant IDs."""
        if not tenant_ids:
            return {}
        
        result = await self.db.execute(
            select(Location.tenant_id, func.count(Location.id))
            .where(Location.tenant_id.in_(tenant_ids))
            .group_by(Location.tenant_id)
        )
        
        return {tenant_id: count for tenant_id, count in result.fetchall()}
