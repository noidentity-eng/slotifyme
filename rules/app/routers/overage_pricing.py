"""Overage pricing router for managing overage pricing references."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_internal_service
from app.services.entitlement_service import EntitlementService
from app.schemas.overage_pricing import OveragePriceRefsUpdate, OveragePriceRefsResponse
from app.models.overage_price_refs import OveragePriceRefs
from app.cache import delete_cached_entitlements
from app.events import emit_addon_changed

router = APIRouter(prefix="/tenants", tags=["tenant"])


@router.put("/{tenant_id}/overage-pricing-refs", response_model=OveragePriceRefsResponse)
async def update_overage_pricing_refs(
    tenant_id: str,
    refs_data: OveragePriceRefsUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_internal_service),
):
    """Update tenant overage pricing references."""
    entitlement_service = EntitlementService(db)
    
    # Ensure tenant has a plan
    tenant_plan = entitlement_service.get_tenant_plan(tenant_id)
    if not tenant_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    # Get or create overage refs
    overage_refs = db.query(OveragePriceRefs).filter(
        OveragePriceRefs.tenant_id == tenant_id
    ).first()
    
    if not overage_refs:
        overage_refs = OveragePriceRefs(
            tenant_id=tenant_id,
            per_stylist_ref="pricebook/overage/stylist@v1",
            per_location_ref="pricebook/overage/location@v1"
        )
        db.add(overage_refs)
    
    # Update fields if provided
    if refs_data.per_stylist_ref is not None:
        overage_refs.per_stylist_ref = refs_data.per_stylist_ref
    
    if refs_data.per_location_ref is not None:
        overage_refs.per_location_ref = refs_data.per_location_ref
    
    # Bump version
    tenant_plan.version += 1
    
    db.commit()
    db.refresh(overage_refs)
    db.refresh(tenant_plan)
    
    # Bust cache
    await delete_cached_entitlements(tenant_id)
    
    # Emit event
    await emit_addon_changed(tenant_id, {"overage_pricing_refs_updated": True})
    
    return overage_refs
