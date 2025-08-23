"""Common schemas used across the service."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response."""
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class SuccessResponse(BaseModel):
    """Standard success response."""
    success: bool = Field(True, description="Success indicator")
    message: Optional[str] = Field(None, description="Success message")


class BaseModelWithTimestamps(BaseModel):
    """Base model with timestamp fields."""
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class AddressSchema(BaseModel):
    """Address schema for locations."""
    line1: str = Field(..., description="Address line 1")
    line2: Optional[str] = Field(None, description="Address line 2")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State/province")
    postal_code: str = Field(..., description="Postal code")
    country: str = Field(default="US", description="Country code")


class ThemeSchema(BaseModel):
    """Theme schema for tenant branding."""
    primary_color: Optional[str] = Field(None, description="Primary brand color")
    secondary_color: Optional[str] = Field(None, description="Secondary brand color")
    logo_url: Optional[str] = Field(None, description="Logo URL")
    font_family: Optional[str] = Field(None, description="Primary font family")
