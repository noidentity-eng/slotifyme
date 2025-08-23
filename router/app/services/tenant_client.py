"""Client for Tenant service integration."""

import httpx
from typing import Optional

from app.config import settings
from app.logging import get_logger

logger = get_logger(__name__)


class TenantClient:
    """Client for Tenant service operations."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.timeout = 5.0  # 5 second timeout
    
    async def tenant_exists(self, tenant_id: str) -> bool:
        """Check if a tenant exists."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/tenants/{tenant_id}")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Tenant existence check failed for {tenant_id}: {e}")
            return False
    
    async def location_exists(self, location_id: str) -> bool:
        """Check if a location exists."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/locations/{location_id}")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Location existence check failed for {location_id}: {e}")
            return False


def get_tenant_client() -> Optional[TenantClient]:
    """Get tenant client if configured."""
    if not settings.tenant_base_url:
        return None
    
    return TenantClient(settings.tenant_base_url)
