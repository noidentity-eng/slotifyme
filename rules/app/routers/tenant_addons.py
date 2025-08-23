"""Tenant addons router for addon assignments."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_internal_service
from app.services.addon_service import AddonService
from app.services.entitlement_service import EntitlementService
from app.schemas.tenant import TenantAddonUpdate, TenantAssignmentsResponse
from app.models.tenant_addon import TenantAddon
from app.cache import delete_cached_entitlements
from app.events import emit_addon_changed

router = APIRouter(prefix="/tenants", tags=["tenant"])


@router.put("/{tenant_id}/addons", response_model=TenantAssignmentsResponse)
async def update_tenant_addons(
    tenant_id: str,
    addon_data: TenantAddonUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_internal_service),
):
    """Update tenant addon assignments."""
    entitlement_service = EntitlementService(db)
    
    # Ensure tenant has a plan
    tenant_plan = entitlement_service.get_tenant_plan(tenant_id)
    if not tenant_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    changes = {}
    version_bumped = False
    
    # Handle add operations
    if addon_data.add:
        addon_service = AddonService(db)
        for addon_code in addon_data.add:
            # Verify addon exists
            addon = addon_service.get_addon(addon_code)
            if not addon:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Addon {addon_code} not found",
                )
            
            # Check if already exists
            existing = db.query(TenantAddon).filter(
                TenantAddon.tenant_id == tenant_id,
                TenantAddon.addon_code == addon_code
            ).first()
            
            if not existing:
                tenant_addon = TenantAddon(
                    tenant_id=tenant_id,
                    addon_code=addon_code,
                    qty=1,
                    meta_json={},
                    pricing_ref=None,
                )
                db.add(tenant_addon)
                changes[f"added_{addon_code}"] = True
                version_bumped = True
    
    # Handle remove operations
    if addon_data.remove:
        for addon_code in addon_data.remove:
            existing = db.query(TenantAddon).filter(
                TenantAddon.tenant_id == tenant_id,
                TenantAddon.addon_code == addon_code
            ).first()
            
            if existing:
                db.delete(existing)
                changes[f"removed_{addon_code}"] = True
                version_bumped = True
    
    # Handle upsert operations
    if addon_data.upsert:
        for item in addon_data.upsert:
            # Verify addon exists
            addon_service = AddonService(db)
            addon = addon_service.get_addon(item.code)
            if not addon:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Addon {item.code} not found",
                )
            
            existing = db.query(TenantAddon).filter(
                TenantAddon.tenant_id == tenant_id,
                TenantAddon.addon_code == item.code
            ).first()
            
            if existing:
                # Update existing
                existing.qty = item.qty
                existing.meta_json = item.meta
                existing.pricing_ref = item.pricing_ref
                changes[f"updated_{item.code}"] = True
            else:
                # Create new
                tenant_addon = TenantAddon(
                    tenant_id=tenant_id,
                    addon_code=item.code,
                    qty=item.qty,
                    meta_json=item.meta,
                    pricing_ref=item.pricing_ref,
                )
                db.add(tenant_addon)
                changes[f"added_{item.code}"] = True
            
            version_bumped = True
    
    # Bump version if there were changes
    if version_bumped:
        tenant_plan.version += 1
    
    db.commit()
    db.refresh(tenant_plan)
    
    # Bust cache
    await delete_cached_entitlements(tenant_id)
    
    # Emit event if there were changes
    if changes:
        await emit_addon_changed(tenant_id, changes)
    
    # Return current assignments
    tenant_addons = entitlement_service.get_tenant_addons(tenant_id)
    addons_data = []
    for addon in tenant_addons:
        addons_data.append({
            "code": addon.addon_code,
            "qty": addon.qty,
            "meta": addon.meta_json,
        })
    
    overrides = entitlement_service.get_tenant_overrides(tenant_id)
    overrides_data = {override.key: override.value_json for override in overrides}
    
    return TenantAssignmentsResponse(
        tenant_id=tenant_id,
        plan={
            "code": tenant_plan.plan_code,
            "meta": tenant_plan.meta_json,
            "version": tenant_plan.version,
        },
        addons=addons_data,
        overrides=overrides_data,
        version=tenant_plan.version,
        created_at=tenant_plan.created_at,
        updated_at=tenant_plan.updated_at,
    )
