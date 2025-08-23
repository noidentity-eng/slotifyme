"""Price preview router for optional pricing integration."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db import get_db
from app.deps import require_internal_service
from app.services.entitlement_service import EntitlementService
from app.schemas.price_preview import PricePreviewResponse, PriceItem, AddonPriceItem, OveragePriceItem
from app.clients.pricing_client import pricing_client

router = APIRouter(prefix="/tenants", tags=["tenant"])


@router.get("/{tenant_id}/price-preview", response_model=PricePreviewResponse)
async def get_price_preview(
    tenant_id: str,
    stylists: Optional[int] = Query(None, description="Number of stylists for overage calculation"),
    locations: Optional[int] = Query(None, description="Number of locations for overage calculation"),
    db: Session = Depends(get_db),
    _: str = Depends(require_internal_service),
):
    """Get price preview for a tenant."""
    entitlement_service = EntitlementService(db)
    
    # Get entitlements
    try:
        entitlements = entitlement_service.compute_entitlements(tenant_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    
    # Collect all pricing refs to resolve
    refs_to_resolve = [entitlements.pricing_refs["plan"]]
    refs_to_resolve.extend(entitlements.pricing_refs["addons"].values())
    refs_to_resolve.extend(entitlements.pricing_refs["overage"].values())
    
    # Resolve prices
    resolved_prices = await pricing_client.resolve_refs_batch(refs_to_resolve)
    
    # Build plan price
    plan_ref = entitlements.pricing_refs["plan"]
    plan_price_data = resolved_prices.get(plan_ref, {})
    plan_price = PriceItem(
        ref=plan_ref,
        amount_dollars=plan_price_data.get("amount_dollars") if plan_price_data else None
    )
    
    # Build addon prices
    addon_prices = []
    for code, ref in entitlements.pricing_refs["addons"].items():
        if ref:
            addon_price_data = resolved_prices.get(ref, {})
            addon_prices.append(AddonPriceItem(
                code=code,
                ref=ref,
                amount_dollars=addon_price_data.get("amount_dollars") if addon_price_data else None
            ))
    
    # Build overage prices
    overage_prices = []
    if stylists is not None or locations is not None:
        # Calculate stylist overage
        if stylists is not None:
            stylist_limit = entitlements.limits.get("stylists", 0)
            stylist_overage = max(0, stylists - stylist_limit)
            if stylist_overage > 0:
                stylist_ref = entitlements.pricing_refs["overage"]["per_stylist"]
                stylist_rate_data = resolved_prices.get(stylist_ref, {})
                stylist_rate_dollars = stylist_rate_data.get("amount_dollars") if stylist_rate_data else None
                stylist_subtotal = stylist_rate_dollars * stylist_overage if stylist_rate_dollars else None
                
                overage_prices.append(OveragePriceItem(
                    kind="per_stylist",
                    units=stylist_overage,
                    rate_ref=stylist_ref,
                    rate_dollars=stylist_rate_dollars,
                    subtotal_dollars=stylist_subtotal
                ))
        
        # Calculate location overage
        if locations is not None:
            location_limit = entitlements.limits.get("locations", 0)
            location_overage = max(0, locations - location_limit)
            if location_overage > 0:
                location_ref = entitlements.pricing_refs["overage"]["per_location"]
                location_rate_data = resolved_prices.get(location_ref, {})
                location_rate_dollars = location_rate_data.get("amount_dollars") if location_rate_data else None
                location_subtotal = location_rate_dollars * location_overage if location_rate_dollars else None
                
                overage_prices.append(OveragePriceItem(
                    kind="per_location",
                    units=location_overage,
                    rate_ref=location_ref,
                    rate_dollars=location_rate_dollars,
                    subtotal_dollars=location_subtotal
                ))
    
    # Calculate total
    total_dollars = None
    if plan_price.amount_dollars is not None:
        total_dollars = plan_price.amount_dollars
        
        for addon in addon_prices:
            if addon.amount_dollars is not None:
                total_dollars += addon.amount_dollars
        
        for overage in overage_prices:
            if overage.subtotal_dollars is not None:
                total_dollars += overage.subtotal_dollars
    
    return PricePreviewResponse(
        plan=plan_price,
        addons=addon_prices,
        overages=overage_prices,
        total_dollars=total_dollars
    )
