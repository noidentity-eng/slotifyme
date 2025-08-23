"""Pydantic schemas for slug mapping operations."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from pydantic import ConfigDict

from app.models.slug_map import ResourceType, SlugStatus


class SlugMapBase(BaseModel):
    """Base schema for slug mapping fields."""
    
    host: str = Field(..., description="Domain name", example="slotifyme.com")
    path: str = Field(..., description="URL path with leading slash", example="/barbershop-a/downtown")
    resource_type: ResourceType = Field(..., description="Type of resource being mapped")
    resource_id: str = Field(..., description="Canonical ID from owning service", example="loc_456")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for convenience", example="ten_123")
    canonical_url: str = Field(..., description="SEO-friendly canonical URL", example="https://slotifyme.com/barbershop-a/downtown")
    status: SlugStatus = Field(SlugStatus.ACTIVE, description="Status of the slug mapping")
    
    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate and normalize path."""
        if not v.startswith("/"):
            raise ValueError("Path must start with /")
        if " " in v:
            raise ValueError("Path cannot contain spaces")
        # Normalize trailing slash
        return v.rstrip("/") if v != "/" else v
    
    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate host format."""
        if not v or "." not in v:
            raise ValueError("Host must be a valid domain name")
        return v.lower()


class SlugMapCreate(SlugMapBase):
    """Schema for creating a new slug mapping."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "host": "slotifyme.com",
                "path": "/barbershop-a/downtown",
                "resource_type": "location",
                "resource_id": "loc_456",
                "tenant_id": "ten_123",
                "canonical_url": "https://slotifyme.com/barbershop-a/downtown",
                "status": "active"
            }
        }
    )


class SlugMapUpdate(BaseModel):
    """Schema for updating a slug mapping."""
    
    host: Optional[str] = Field(None, description="Domain name")
    path: Optional[str] = Field(None, description="URL path with leading slash")
    resource_type: Optional[ResourceType] = Field(None, description="Type of resource being mapped")
    resource_id: Optional[str] = Field(None, description="Canonical ID from owning service")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for convenience")
    canonical_url: Optional[str] = Field(None, description="SEO-friendly canonical URL")
    status: Optional[SlugStatus] = Field(None, description="Status of the slug mapping")
    
    @field_validator("path")
    @classmethod
    def validate_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize path."""
        if v is None:
            return v
        if not v.startswith("/"):
            raise ValueError("Path must start with /")
        if " " in v:
            raise ValueError("Path cannot contain spaces")
        return v.rstrip("/") if v != "/" else v
    
    @field_validator("host")
    @classmethod
    def validate_host(cls, v: Optional[str]) -> Optional[str]:
        """Validate host format."""
        if v is None:
            return v
        if not v or "." not in v:
            raise ValueError("Host must be a valid domain name")
        return v.lower()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "canonical_url": "https://slotifyme.com/barbershop-a/downtown-location"
            }
        }
    )


class SlugMapResponse(SlugMapBase):
    """Schema for slug mapping response."""
    
    id: str = Field(..., description="Unique identifier")
    version: int = Field(..., description="Version number for cache invalidation")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class SlugMapListResponse(BaseModel):
    """Schema for paginated slug mapping list response."""
    
    items: list[SlugMapResponse] = Field(..., description="List of slug mappings")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class SlugAvailabilityResponse(BaseModel):
    """Schema for slug availability check response."""
    
    available: bool = Field(..., description="Whether the slug is available")
    conflicting_id: Optional[str] = Field(None, description="ID of conflicting slug if not available")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "available": False,
                "conflicting_id": "slug_123"
            }
        }
    )
