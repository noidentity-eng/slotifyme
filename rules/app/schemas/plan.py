"""Plan schemas for API requests and responses."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class PlanBase(BaseModel):
    """Base plan schema."""
    code: str = Field(..., description="Plan code (e.g., 'silver', 'gold', 'platinum')")
    name: str = Field(..., description="Plan name")
    limits_json: Dict[str, Any] = Field(default_factory=dict, description="Plan limits")
    features_json: Dict[str, Any] = Field(default_factory=dict, description="Plan features")
    overage_policy_json: Dict[str, Any] = Field(default_factory=dict, description="Overage policy")
    pricing_ref: Optional[str] = Field(None, description="Pricing reference")


class PlanCreate(PlanBase):
    """Schema for creating a plan."""
    pass


class PlanUpdate(BaseModel):
    """Schema for updating a plan."""
    name: str = Field(..., description="Plan name")
    limits_json: Dict[str, Any] = Field(..., description="Plan limits")
    features_json: Dict[str, Any] = Field(..., description="Plan features")
    overage_policy_json: Dict[str, Any] = Field(..., description="Overage policy")
    pricing_ref: Optional[str] = Field(None, description="Pricing reference")


class PlanResponse(PlanBase):
    """Schema for plan response."""
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PlanList(BaseModel):
    """Schema for list of plans."""
    plans: List[PlanResponse]
    total: int
