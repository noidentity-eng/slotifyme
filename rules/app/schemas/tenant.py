"""Tenant assignment schemas for API requests and responses."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class TenantPlanUpdate(BaseModel):
    """Schema for updating tenant plan."""
    plan_code: str = Field(..., description="Plan code to assign")
    pricing_ref: Optional[str] = Field(None, description="Pricing reference override")
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Plan metadata")


class TenantAddonItem(BaseModel):
    """Schema for tenant addon item."""
    code: str = Field(..., description="Addon code")
    qty: int = Field(default=1, description="Addon quantity")
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Addon metadata")
    pricing_ref: Optional[str] = Field(None, description="Pricing reference override")


class TenantAddonUpdate(BaseModel):
    """Schema for updating tenant addons."""
    add: Optional[List[str]] = Field(default_factory=list, description="Addon codes to add")
    remove: Optional[List[str]] = Field(default_factory=list, description="Addon codes to remove")
    upsert: Optional[List[TenantAddonItem]] = Field(default_factory=list, description="Addons to upsert")


class TenantLimitOverrideUpdate(BaseModel):
    """Schema for updating tenant limit overrides."""
    upsert: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Overrides to upsert")
    remove: Optional[List[str]] = Field(default_factory=list, description="Override keys to remove")


class TenantAssignmentsResponse(BaseModel):
    """Schema for tenant assignments response."""
    tenant_id: str
    plan: Optional[Dict[str, Any]] = None
    addons: List[Dict[str, Any]] = []
    overrides: Dict[str, Any] = {}
    version: int
    created_at: datetime
    updated_at: datetime
