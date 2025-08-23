"""Entitlement service for computing tenant entitlements."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.plan import Plan
from app.models.addon import Addon
from app.models.tenant_plan import TenantPlan
from app.models.tenant_addon import TenantAddon
from app.models.limit_override import TenantLimitOverride
from app.schemas.entitlements import EntitlementsResponse
from app.config import settings


class EntitlementService:
    """Service for computing tenant entitlements."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def compute_entitlements(self, tenant_id: str) -> EntitlementsResponse:
        """Compute entitlements for a tenant."""
        # Get tenant plan
        tenant_plan = self.db.query(TenantPlan).filter(TenantPlan.tenant_id == tenant_id).first()
        if not tenant_plan:
            raise ValueError(f"Tenant {tenant_id} has no plan assigned")
        
        # Get plan details
        plan = self.db.query(Plan).filter(Plan.code == tenant_plan.plan_code).first()
        if not plan:
            raise ValueError(f"Plan {tenant_plan.plan_code} not found")
        
        # Get tenant addons
        tenant_addons = self.db.query(TenantAddon).filter(TenantAddon.tenant_id == tenant_id).all()
        addon_codes = [ta.addon_code for ta in tenant_addons]
        
        # Get addon details
        addons = self.db.query(Addon).filter(Addon.code.in_(addon_codes)).all()
        addon_map = {addon.code: addon for addon in addons}
        
        # Get overrides
        overrides = self.db.query(TenantLimitOverride).filter(
            TenantLimitOverride.tenant_id == tenant_id
        ).all()
        override_map = {override.key: override.value_json for override in overrides}
        
        # Compute entitlements
        entitlements = self._compute_entitlements(
            plan, tenant_addons, addon_map, override_map, tenant_plan
        )
        
        return entitlements
    
    def _compute_entitlements(
        self,
        plan: Plan,
        tenant_addons: List[TenantAddon],
        addon_map: Dict[str, Addon],
        override_map: Dict[str, Any],
        tenant_plan: TenantPlan,
    ) -> EntitlementsResponse:
        """Compute entitlements from plan, addons, and overrides."""
        
        # Start with plan limits and features
        limits = plan.limits_json.copy()
        features = plan.features_json.copy()
        overage_policy = plan.overage_policy_json.copy()
        
        # Rename limits to match new schema
        if "locations_included" in limits:
            limits["locations"] = limits.pop("locations_included")
        if "stylists_included" in limits:
            limits["stylists"] = limits.pop("stylists_included")
        
        # Initialize all possible features to False
        all_features = {
            "basic_reporting": False,
            "family_booking": False,
            "loyalty_points": False,
            "reviews": False,
            "advanced_analytics": False,
            "stylist_matching": False,
            "ai_booking": False,
            "variable_pricing": False,
            "packages": False,
            "upsell": False,
            "waitlist": False,
            "gift_cards": False,
            "online_store": False,
            "tiered_loyalty": False,
            "memberships": False,
            "smart_no_shows": False,
            "dynamic_pricing": False,
            "ai_promotions": False,
            "staff_utilization": False,
            "offline_mode": False,
            "data_export": False,
            "voice_assistant": False,
        }
        
        # Update with plan features
        all_features.update(features)
        features = all_features
        
        # Apply addon effects using effect_json
        for tenant_addon in tenant_addons:
            addon = addon_map.get(tenant_addon.addon_code)
            if not addon:
                continue
            
            # Apply the addon's effect_json to features
            for feature, value in addon.effect_json.items():
                if isinstance(value, bool):
                    features[feature] = value
        
        # Apply overrides (overrides take precedence)
        for key, value in override_map.items():
            # Handle limit overrides (check both old and new names)
            if key == "locations_included":
                limits["locations"] = value
            elif key == "stylists_included":
                limits["stylists"] = value
            elif key in limits:
                limits[key] = value
            elif key in features:
                features[key] = value
            else:
                # Generic override
                if key in limits:
                    limits[key] = value
                elif key in features:
                    features[key] = value
        
        # Build pricing references
        from app.models.overage_price_refs import OveragePriceRefs
        
        # Get overage pricing refs (create defaults if absent)
        overage_refs = self.db.query(OveragePriceRefs).filter(
            OveragePriceRefs.tenant_id == tenant_plan.tenant_id
        ).first()
        
        if not overage_refs:
            overage_refs = OveragePriceRefs(
                tenant_id=tenant_plan.tenant_id,
                per_stylist_ref="pricebook/overage/stylist@v1",
                per_location_ref="pricebook/overage/location@v1"
            )
            self.db.add(overage_refs)
            self.db.commit()
            self.db.refresh(overage_refs)
        
        # Build pricing_refs structure
        pricing_refs = {
            "plan": tenant_plan.pricing_ref or plan.pricing_ref or "",
            "addons": {},
            "overage": {
                "per_stylist": overage_refs.per_stylist_ref or "pricebook/overage/stylist@v1",
                "per_location": overage_refs.per_location_ref or "pricebook/overage/location@v1"
            }
        }
        
        # Add addon pricing refs
        for tenant_addon in tenant_addons:
            addon = addon_map.get(tenant_addon.addon_code)
            if addon:
                pricing_refs["addons"][addon.code] = (
                    tenant_addon.pricing_ref or addon.pricing_ref or ""
                )
        
        return EntitlementsResponse(
            tenant_id=tenant_plan.tenant_id,
            plan=plan.code,
            limits=limits,
            features=features,
            overage_policy=overage_policy,
            pricing_refs=pricing_refs,
            version=tenant_plan.version,
            updated_at=tenant_plan.updated_at,
            ttl_hint_sec=settings.cache_ttl_seconds,
        )
    
    def get_tenant_plan(self, tenant_id: str) -> Optional[TenantPlan]:
        """Get tenant plan."""
        return self.db.query(TenantPlan).filter(TenantPlan.tenant_id == tenant_id).first()
    
    def get_tenant_addons(self, tenant_id: str) -> List[TenantAddon]:
        """Get tenant addons."""
        return self.db.query(TenantAddon).filter(TenantAddon.tenant_id == tenant_id).all()
    
    def get_tenant_overrides(self, tenant_id: str) -> List[TenantLimitOverride]:
        """Get tenant overrides."""
        return self.db.query(TenantLimitOverride).filter(
            TenantLimitOverride.tenant_id == tenant_id
        ).all()
