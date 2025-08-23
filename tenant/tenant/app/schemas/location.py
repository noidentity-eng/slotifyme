"""Location-related schemas."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from tenant.app.models.location import LocationStatus
from tenant.app.schemas.common import BaseModelWithTimestamps, AddressSchema
import pytz


class LocationCreate(BaseModel):
    """Schema for creating a location."""
    name: str = Field(..., min_length=1, max_length=255, description="Location name")
    slug: Optional[str] = Field(None, min_length=2, max_length=50, description="Location slug (auto-generated if not provided)")
    address: Optional[AddressSchema] = Field(None, description="Location address")
    timezone: str = Field(..., description="IANA timezone (e.g., America/Los_Angeles)")
    phone: Optional[str] = Field(None, description="Phone number")
    phone_public: bool = Field(default=False, description="Whether phone is publicly visible")
    status: LocationStatus = Field(default=LocationStatus.ACTIVE, description="Location status")
    
    @validator('timezone')
    def validate_timezone(cls, v):
        """Validate that timezone is a valid IANA timezone."""
        if v not in pytz.all_timezones:
            raise ValueError(f"Invalid timezone: {v}")
        return v


class LocationUpdate(BaseModel):
    """Schema for updating a location."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Location name")
    address: Optional[AddressSchema] = Field(None, description="Location address")
    timezone: Optional[str] = Field(None, description="IANA timezone")
    phone: Optional[str] = Field(None, description="Phone number")
    phone_public: Optional[bool] = Field(None, description="Whether phone is publicly visible")
    status: Optional[LocationStatus] = Field(None, description="Location status")
    
    @validator('timezone')
    def validate_timezone(cls, v):
        """Validate that timezone is a valid IANA timezone."""
        if v is not None and v not in pytz.all_timezones:
            raise ValueError(f"Invalid timezone: {v}")
        return v


class LocationResponse(BaseModel):
    """Schema for location response."""
    location_id: str = Field(..., description="Location ID")
    tenant_id: str = Field(..., description="Tenant ID")
    slug: str = Field(..., description="Location slug")
    name: str = Field(..., description="Location name")
    address: Optional[AddressSchema] = Field(None, description="Location address")
    timezone: str = Field(..., description="IANA timezone")
    phone: Optional[str] = Field(None, description="Phone number")
    phone_public: bool = Field(..., description="Whether phone is publicly visible")
    status: LocationStatus = Field(..., description="Location status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class LocationCreateResponse(BaseModel):
    """Schema for location creation response."""
    location_id: str = Field(..., description="Location ID")
    slug: str = Field(..., description="Location slug")


class LocationListResponse(BaseModel):
    """Schema for location list response."""
    location_id: str = Field(..., description="Location ID")
    slug: str = Field(..., description="Location slug")
    name: str = Field(..., description="Location name")
    timezone: str = Field(..., description="IANA timezone")
    phone_public: bool = Field(..., description="Whether phone is publicly visible")
    status: LocationStatus = Field(..., description="Location status")


# Public schemas (for public endpoints)
class PublicLocationResponse(BaseModel):
    """Public location response (limited fields)."""
    id: str = Field(..., description="Location ID")
    tenant_slug: str = Field(..., description="Tenant slug")
    location_slug: str = Field(..., description="Location slug")
    name: str = Field(..., description="Location name")
    timezone: str = Field(..., description="IANA timezone")
    phone_public: bool = Field(..., description="Whether phone is publicly visible")
    phone: Optional[str] = Field(None, description="Phone number (only if phone_public is true)")
    status: LocationStatus = Field(..., description="Location status")


class PublicLocationListResponse(BaseModel):
    """Public location list response."""
    tenant_slug: str = Field(..., description="Tenant slug")
    locations: list[PublicLocationResponse] = Field(..., description="List of locations")
