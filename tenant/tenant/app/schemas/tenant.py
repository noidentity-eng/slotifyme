"""Tenant-related schemas."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from tenant.app.models.tenant import TenantStatus
from tenant.app.schemas.common import BaseModelWithTimestamps, ThemeSchema


class TenantCreate(BaseModel):
    """Schema for creating a tenant."""
    name: str = Field(..., min_length=1, max_length=255, description="Tenant name")
    slug: Optional[str] = Field(None, min_length=2, max_length=50, description="Tenant slug (auto-generated if not provided)")
    theme: Optional[ThemeSchema] = Field(None, description="Tenant theme/branding")


class TenantUpdate(BaseModel):
    """Schema for updating a tenant."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Tenant name")
    status: Optional[TenantStatus] = Field(None, description="Tenant status")
    theme: Optional[ThemeSchema] = Field(None, description="Tenant theme/branding")


class TenantResponse(BaseModel):
    """Schema for tenant response."""
    tenant_id: str = Field(..., description="Tenant ID")
    name: str = Field(..., description="Tenant name")
    slug: str = Field(..., description="Tenant slug")
    status: TenantStatus = Field(..., description="Tenant status")
    theme: Optional[ThemeSchema] = Field(None, description="Tenant theme")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class TenantCreateResponse(BaseModel):
    """Schema for tenant creation response."""
    tenant_id: str = Field(..., description="Tenant ID")
    name: str = Field(..., description="Tenant name")
    slug: str = Field(..., description="Tenant slug")


class TenantListResponse(BaseModel):
    """Schema for tenant list response."""
    tenant_id: str = Field(..., description="Tenant ID")
    name: str = Field(..., description="Tenant name")
    slug: str = Field(..., description="Tenant slug")
    status: TenantStatus = Field(..., description="Tenant status")
    locations_count: int = Field(..., description="Number of locations")
    owner_emails: Optional[List[str]] = Field(None, description="Owner email addresses")


class TenantListQuery(BaseModel):
    """Schema for tenant list query parameters."""
    q: Optional[str] = Field(None, description="Search query for name or slug")
    status: Optional[TenantStatus] = Field(None, description="Filter by status")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


# Public schemas (for public endpoints)
class PublicTenantResponse(BaseModel):
    """Public tenant response (limited fields)."""
    id: str = Field(..., description="Tenant ID")
    slug: str = Field(..., description="Tenant slug")
    name: str = Field(..., description="Tenant name")
    theme: Optional[ThemeSchema] = Field(None, description="Tenant theme")
