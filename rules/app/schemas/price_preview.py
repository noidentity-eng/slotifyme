"""Price preview schemas for API responses."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class PriceItem(BaseModel):
    """Schema for a price item."""
    ref: str = Field(..., description="Pricing reference")
    amount_dollars: Optional[float] = Field(None, description="Amount in dollars")


class AddonPriceItem(BaseModel):
    """Schema for an addon price item."""
    code: str = Field(..., description="Addon code")
    ref: str = Field(..., description="Pricing reference")
    amount_dollars: Optional[float] = Field(None, description="Amount in dollars")


class OveragePriceItem(BaseModel):
    """Schema for an overage price item."""
    kind: str = Field(..., description="Overage kind (per_stylist, per_location)")
    units: int = Field(..., description="Number of overage units")
    rate_ref: str = Field(..., description="Rate pricing reference")
    rate_dollars: Optional[float] = Field(None, description="Rate amount in dollars")
    subtotal_dollars: Optional[float] = Field(None, description="Subtotal amount in dollars")


class PricePreviewResponse(BaseModel):
    """Schema for price preview response."""
    plan: PriceItem
    addons: List[AddonPriceItem] = []
    overages: List[OveragePriceItem] = []
    total_dollars: Optional[float] = Field(None, description="Total amount in dollars")
    
    class Config:
        json_schema_extra = {
            "example": {
                "plan": {
                    "ref": "pricebook/plans/gold@v2",
                    "amount_dollars": 199.00
                },
                "addons": [
                    {
                        "code": "ai_booking",
                        "ref": "pricebook/addons/ai_booking@v1",
                        "amount_dollars": 49.99
                    },
                    {
                        "code": "value_pack",
                        "ref": "pricebook/addons/value_pack@v2",
                        "amount_dollars": 49.99
                    }
                ],
                "overages": [
                    {
                        "kind": "per_stylist",
                        "units": 2,
                        "rate_ref": "pricebook/overage/stylist@v1",
                        "rate_dollars": 15.00,
                        "subtotal_dollars": 30.00
                    },
                    {
                        "kind": "per_location",
                        "units": 1,
                        "rate_ref": "pricebook/overage/location@v1",
                        "rate_dollars": 99.00,
                        "subtotal_dollars": 99.00
                    }
                ],
                "total_dollars": 199.00 + 49.99 + 49.99 + 30.00 + 99.00
            }
        }
