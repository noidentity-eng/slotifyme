"""Tenant plan router for plan assignments."""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_internal_service
from app.services.plan_service import PlanService
from app.services.entitlement_service import EntitlementService
from app.schemas.tenant import TenantPlanUpdate, TenantAssignmentsResponse
from app.utils.versioning import bump_tenant_version
from app.cache import delete_cached_entitlements
from app.events import emit_plan_changed

router = APIRouter(prefix="/tenants", tags=["tenant"])


@router.put("/{tenant_id}/plan", response_model=TenantAssignmentsResponse)
async def update_tenant_plan(
    tenant_id: str,
    plan_data: TenantPlanUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_internal_service),
):
    """Update tenant plan assignment."""
    # Verify plan exists
    plan_service = PlanService(db)
    plan = plan_service.get_plan(plan_data.plan_code)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )
    
    # Get current plan for event emission
    entitlement_service = EntitlementService(db)
    current_plan = entitlement_service.get_tenant_plan(tenant_id)
    old_plan_code = current_plan.plan_code if current_plan else None
    
    # Update or create tenant plan
    if current_plan:
        current_plan.plan_code = plan_data.plan_code
        current_plan.pricing_ref = plan_data.pricing_ref
        current_plan.meta_json = plan_data.meta
        current_plan.version += 1
    else:
        from app.models.tenant_plan import TenantPlan
        current_plan = TenantPlan(
            tenant_id=tenant_id,
            plan_code=plan_data.plan_code,
            pricing_ref=plan_data.pricing_ref,
            meta_json=plan_data.meta,
            version=1,
        )
        db.add(current_plan)
    
    db.commit()
    db.refresh(current_plan)
    
    # Bust cache
    await delete_cached_entitlements(tenant_id)
    
    # Emit event
    await emit_plan_changed(tenant_id, old_plan_code, plan_data.plan_code)
    
    # Return current assignments
    return TenantAssignmentsResponse(
        tenant_id=tenant_id,
        plan={
            "code": current_plan.plan_code,
            "meta": current_plan.meta_json,
            "version": current_plan.version,
        },
        addons=[],
        overrides={},
        version=current_plan.version,
        created_at=current_plan.created_at,
        updated_at=current_plan.updated_at,
    )


@router.get("/{tenant_id}/assignments", response_model=TenantAssignmentsResponse)
async def get_tenant_assignments(
    tenant_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(require_internal_service),
):
    """Get current tenant assignments."""
    entitlement_service = EntitlementService(db)
    
    # Get tenant plan
    tenant_plan = entitlement_service.get_tenant_plan(tenant_id)
    if not tenant_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    # Get tenant addons
    tenant_addons = entitlement_service.get_tenant_addons(tenant_id)
    addons_data = []
    for addon in tenant_addons:
        addons_data.append({
            "code": addon.addon_code,
            "qty": addon.qty,
            "meta": addon.meta_json,
        })
    
    # Get overrides
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
