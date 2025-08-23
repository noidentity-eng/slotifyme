"""Pydantic schemas for resolve operations."""

from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.slug_map import ResourceType


class ResourceInfo(BaseModel):
    """Schema for resource information in resolve response."""
    
    type: ResourceType = Field(..., description="Type of resource")
    id: str = Field(..., description="Resource ID")
    
    model_config = ConfigDict(from_attributes=True)


class CacheInfo(BaseModel):
    """Schema for cache information in resolve response."""
    
    max_age: int = Field(..., description="Cache max age in seconds")
    etag: str = Field(..., description="ETag for cache validation")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "max_age": 600,
                "etag": "W/\"loc_456-v3\""
            }
        }
    )


class ResolveResponse(BaseModel):
    """Schema for resolve response."""
    
    match: bool = Field(..., description="Whether a match was found")
    resource: Optional[ResourceInfo] = Field(None, description="Resource information if match found")
    tenant_id: Optional[str] = Field(None, description="Tenant ID if available")
    version: Optional[int] = Field(None, description="Version number for cache invalidation")
    canonical_url: Optional[str] = Field(None, description="Canonical URL if available")
    cache: Optional[CacheInfo] = Field(None, description="Cache information")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "match": True,
                "resource": {
                    "type": "location",
                    "id": "loc_456"
                },
                "tenant_id": "ten_123",
                "version": 3,
                "canonical_url": "https://slotifyme.com/barbershop-a/downtown",
                "cache": {
                    "max_age": 600,
                    "etag": "W/\"loc_456-v3\""
                }
            }
        }
    )
