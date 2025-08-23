"""FastAPI routers for the Rules Service."""

from .health import router as health_router
from .admin_plans import router as admin_plans_router
from .admin_addons import router as admin_addons_router
from .tenant_plan import router as tenant_plan_router
from .tenant_addons import router as tenant_addons_router
from .tenant_overrides import router as tenant_overrides_router
from .overage_pricing import router as overage_pricing_router
from .price_preview import router as price_preview_router
from .entitlements import router as entitlements_router

__all__ = [
    "health_router",
    "admin_plans_router",
    "admin_addons_router", 
    "tenant_plan_router",
    "tenant_addons_router",
    "tenant_overrides_router",
    "overage_pricing_router",
    "price_preview_router",
    "entitlements_router",
]
