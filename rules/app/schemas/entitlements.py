"""Entitlements schema for API responses."""

from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field


class EntitlementsResponse(BaseModel):
    """Schema for entitlements response."""
    tenant_id: str = Field(..., description="Tenant ID")
    plan: str = Field(..., description="Plan code")
    limits: Dict[str, Any] = Field(..., description="Computed limits")
    features: Dict[str, Any] = Field(..., description="Computed features")
    overage_policy: Dict[str, Any] = Field(..., description="Overage policy")
    pricing_refs: Dict[str, Any] = Field(..., description="Pricing references")
    version: int = Field(..., description="Version number")
    updated_at: datetime = Field(..., description="Last updated timestamp")
    ttl_hint_sec: int = Field(..., description="Cache TTL hint in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "ten_123",
                "plan": "gold",
                "limits": {"locations": 2, "stylists": 10},
                "features": {
                    "basic_reporting": True,
                    "family_booking": True,
                    "loyalty_points": True,
                    "reviews": True,
                    "advanced_analytics": True,
                    "stylist_matching": True,
                    "ai_booking": True,
                    "variable_pricing": False,
                    "packages": True,
                    "upsell": True,
                    "waitlist": True,
                    "gift_cards": True
                },
                "overage_policy": {"allow_extra_locations": True, "allow_extra_stylists": True},
                "pricing_refs": {
                    "plan": "pricebook/plans/gold@v2",
                    "addons": {
                        "ai_booking": "pricebook/addons/ai_booking@v1",
                        "variable_pricing": "pricebook/addons/variable_pricing@v1",
                        "value_pack": "pricebook/addons/value_pack@v2"
                    },
                    "overage": {
                        "per_stylist": "pricebook/overage/stylist@v1",
                        "per_location": "pricebook/overage/location@v1"
                    }
                },
                "version": 8,
                "updated_at": "2025-08-21T18:05:00Z",
                "ttl_hint_sec": 900
            }
        }
