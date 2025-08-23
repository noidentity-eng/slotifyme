"""Addon schemas for API requests and responses."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AddonBase(BaseModel):
    """Base addon schema."""
    code: str = Field(..., description="Addon code (e.g., 'ai_booking', 'variable_pricing')")
    name: str = Field(..., description="Addon name")
    meta_json: Dict[str, Any] = Field(default_factory=dict, description="Addon metadata")
    effect_json: Dict[str, Any] = Field(default_factory=dict, description="Addon effect on features")
    pricing_ref: Optional[str] = Field(None, description="Pricing reference")


class AddonCreate(AddonBase):
    """Schema for creating an addon."""
    pass


class AddonUpdate(BaseModel):
    """Schema for updating an addon."""
    name: str = Field(..., description="Addon name")
    meta_json: Dict[str, Any] = Field(..., description="Addon metadata")
    effect_json: Dict[str, Any] = Field(..., description="Addon effect on features")
    pricing_ref: Optional[str] = Field(None, description="Pricing reference")


class AddonResponse(AddonBase):
    """Schema for addon response."""
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AddonList(BaseModel):
    """Schema for list of addons."""
    addons: List[AddonResponse]
    total: int
