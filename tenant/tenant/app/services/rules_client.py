"""Rules client for optional pre-checks."""

from typing import Optional, Dict, Any
import httpx
from tenant.app.config import settings
from tenant.app.logging import get_logger

logger = get_logger(__name__)


class RulesClient:
    """Client for the rules service."""
    
    def __init__(self):
        self.base_url = settings.rules_base_url
        self.timeout = 5.0  # 5 second timeout
    
    async def get_entitlements(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get entitlements for a tenant."""
        if not self.base_url:
            logger.debug("Rules service not configured, skipping entitlements check")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/entitlements/{tenant_id}")
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    logger.warning("Tenant not found in rules service", tenant_id=tenant_id)
                    return None
                else:
                    logger.error("Rules service error", status_code=response.status_code, tenant_id=tenant_id)
                    return None
                    
        except httpx.TimeoutException:
            logger.warning("Rules service timeout, allowing operation", tenant_id=tenant_id)
            return None
        except Exception as e:
            logger.error("Rules service error", error=str(e), tenant_id=tenant_id)
            return None
    
    async def check_location_limit(self, tenant_id: str, current_count: int) -> bool:
        """Check if adding a location would exceed the tenant's limit."""
        entitlements = await self.get_entitlements(tenant_id)
        if not entitlements:
            # If we can't get entitlements, allow the operation
            return True
        
        limits = entitlements.get("limits", {})
        location_limit = limits.get("locations")
        
        if location_limit is None:
            # No limit specified, allow operation
            return True
        
        if current_count + 1 > location_limit:
            overage_policy = entitlements.get("overage_policy", {})
            if not overage_policy.get("extra_locations", False):
                logger.warning("Location limit exceeded", tenant_id=tenant_id, current=current_count, limit=location_limit)
                return False
        
        return True


# Global rules client instance
rules_client = RulesClient()
