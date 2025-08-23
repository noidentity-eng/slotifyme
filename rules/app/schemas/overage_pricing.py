"""Overage pricing schemas for API requests and responses."""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class OveragePriceRefsUpdate(BaseModel):
    """Schema for updating overage pricing references."""
    per_stylist_ref: Optional[str] = Field(None, description="Per stylist pricing reference")
    per_location_ref: Optional[str] = Field(None, description="Per location pricing reference")


class OveragePriceRefsResponse(BaseModel):
    """Schema for overage pricing references response."""
    tenant_id: str
    per_stylist_ref: Optional[str] = None
    per_location_ref: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
