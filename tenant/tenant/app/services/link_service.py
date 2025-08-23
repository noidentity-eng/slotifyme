"""Link service for managing user-tenant relationships."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from tenant.app.models.tenant_user import TenantUser, UserRole
from tenant.app.models.tenant import Tenant
from tenant.app.schemas.link import UserLinkCreate, UserLinkQuery
from tenant.app.logging import get_logger
from tenant.app.services.events import emit_event

logger = get_logger(__name__)


class LinkService:
    """Service for user-tenant linking operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def link_user(self, tenant_id: str, user_data: UserLinkCreate) -> TenantUser:
        """Link a user to a tenant with a specific role."""
        # Verify tenant exists
        tenant = await self._get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")
        
        # Check if user is already linked
        existing_link = await self._get_user_link(tenant_id, user_data.user_id)
        
        if existing_link:
            # Update existing link
            existing_link.role = user_data.role
            await self.db.commit()
            await self.db.refresh(existing_link)
            
            # Emit event
            await emit_event("TenantUserLinked", {
                "tenant_id": tenant_id,
                "user_id": user_data.user_id,
                "role": user_data.role.value
            })
            
            logger.info("Updated user link", tenant_id=tenant_id, user_id=user_data.user_id, role=user_data.role)
            return existing_link
        else:
            # Create new link
            user_link = TenantUser(
                tenant_id=tenant_id,
                user_id=user_data.user_id,
                role=user_data.role
            )
            
            self.db.add(user_link)
            await self.db.commit()
            await self.db.refresh(user_link)
            
            # Emit event
            await emit_event("TenantUserLinked", {
                "tenant_id": tenant_id,
                "user_id": user_data.user_id,
                "role": user_data.role.value
            })
            
            logger.info("Created user link", tenant_id=tenant_id, user_id=user_data.user_id, role=user_data.role)
            return user_link
    
    async def unlink_user(self, tenant_id: str, user_id: str) -> bool:
        """Unlink a user from a tenant."""
        user_link = await self._get_user_link(tenant_id, user_id)
        if not user_link:
            return False
        
        await self.db.delete(user_link)
        await self.db.commit()
        
        # Emit event
        await emit_event("TenantUserUnlinked", {
            "tenant_id": tenant_id,
            "user_id": user_id
        })
        
        logger.info("Unlinked user", tenant_id=tenant_id, user_id=user_id)
        return True
    
    async def list_users(self, tenant_id: str, query: Optional[UserLinkQuery] = None) -> List[TenantUser]:
        """List users linked to a tenant."""
        base_query = select(TenantUser).where(TenantUser.tenant_id == tenant_id)
        
        if query and query.role:
            base_query = base_query.where(TenantUser.role == query.role)
        
        base_query = base_query.order_by(TenantUser.created_at)
        
        result = await self.db.execute(base_query)
        return result.scalars().all()
    
    async def get_tenant_stats(self, tenant_id: str) -> dict:
        """Get statistics for a tenant."""
        # Get location count
        location_count = await self._get_location_count(tenant_id)
        
        # Get user counts by role
        user_counts = await self._get_user_counts(tenant_id)
        
        return {
            "tenant_id": tenant_id,
            "locations": location_count,
            "owners": user_counts.get(UserRole.OWNER, 0),
            "staff": user_counts.get(UserRole.STAFF, 0),
            "stylists": user_counts.get(UserRole.STYLIST, 0)
        }
    
    async def _get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get a tenant by ID."""
        result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_user_link(self, tenant_id: str, user_id: str) -> Optional[TenantUser]:
        """Get a user link by tenant ID and user ID."""
        result = await self.db.execute(
            select(TenantUser).where(
                and_(TenantUser.tenant_id == tenant_id, TenantUser.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()
    
    async def _get_location_count(self, tenant_id: str) -> int:
        """Get the number of locations for a tenant."""
        from tenant.app.models.location import Location
        
        result = await self.db.execute(
            select(func.count(Location.id)).where(Location.tenant_id == tenant_id)
        )
        return result.scalar() or 0
    
    async def _get_user_counts(self, tenant_id: str) -> dict:
        """Get user counts by role for a tenant."""
        result = await self.db.execute(
            select(TenantUser.role, func.count(TenantUser.user_id))
            .where(TenantUser.tenant_id == tenant_id)
            .group_by(TenantUser.role)
        )
        
        return {role: count for role, count in result.fetchall()}
