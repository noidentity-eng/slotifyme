"""Tenant overrides router for limit overrides."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_internal_service
from app.services.entitlement_service import EntitlementService
from app.schemas.tenant import TenantLimitOverrideUpdate, TenantAssignmentsResponse
from app.models.limit_override import TenantLimitOverride
from app.cache import delete_cached_entitlements
from app.events import emit_addon_changed

router = APIRouter(prefix="/tenants", tags=["tenant"])


@router.put("/{tenant_id}/overrides", response_model=TenantAssignmentsResponse)
async def update_tenant_overrides(
    tenant_id: str,
    override_data: TenantLimitOverrideUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_internal_service),
):
    """Update tenant limit overrides."""
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
    
    # Handle upsert operations
    if override_data.upsert:
        for item in override_data.upsert:
            if "key" not in item or "value" not in item:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Override items must have 'key' and 'value' fields",
                )
            
            key = item["key"]
            value = item["value"]
            
            # Find existing override
            existing = db.query(TenantLimitOverride).filter(
                TenantLimitOverride.tenant_id == tenant_id,
                TenantLimitOverride.key == key
            ).first()
            
            if existing:
                # Update existing
                existing.value_json = value
                changes[f"updated_{key}"] = True
            else:
                # Create new
                override = TenantLimitOverride(
                    tenant_id=tenant_id,
                    key=key,
                    value_json=value,
                )
                db.add(override)
                changes[f"added_{key}"] = True
            
            version_bumped = True
    
    # Handle remove operations
    if override_data.remove:
        for key in override_data.remove:
            existing = db.query(TenantLimitOverride).filter(
                TenantLimitOverride.tenant_id == tenant_id,
                TenantLimitOverride.key == key
            ).first()
            
            if existing:
                db.delete(existing)
                changes[f"removed_{key}"] = True
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
