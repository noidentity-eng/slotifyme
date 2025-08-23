"""User linking schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from tenant.app.models.tenant_user import UserRole


class UserLinkCreate(BaseModel):
    """Schema for linking a user to a tenant."""
    user_id: str = Field(..., description="User ID")
    role: UserRole = Field(..., description="User role in the tenant")


class UserLinkResponse(BaseModel):
    """Schema for user link response."""
    tenant_id: str = Field(..., description="Tenant ID")
    user_id: str = Field(..., description="User ID")
    role: UserRole = Field(..., description="User role")
    created_at: datetime = Field(..., description="Link creation timestamp")


class UserLinkListResponse(BaseModel):
    """Schema for user link list response."""
    tenant_id: str = Field(..., description="Tenant ID")
    user_id: str = Field(..., description="User ID")
    role: UserRole = Field(..., description="User role")
    created_at: datetime = Field(..., description="Link creation timestamp")


class UserLinkQuery(BaseModel):
    """Schema for user link query parameters."""
    role: Optional[UserRole] = Field(None, description="Filter by role")


class LinkResponse(BaseModel):
    """Schema for link/unlink operation response."""
    linked: bool = Field(..., description="Whether the user was successfully linked/unlinked")
    message: Optional[str] = Field(None, description="Operation message")


class TenantStatsResponse(BaseModel):
    """Schema for tenant statistics response."""
    tenant_id: str = Field(..., description="Tenant ID")
    locations: int = Field(..., description="Number of locations")
    owners: int = Field(..., description="Number of owners")
    staff: int = Field(..., description="Number of staff")
    stylists: int = Field(..., description="Number of stylists")
