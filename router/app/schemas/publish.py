"""Pydantic schemas for manifest publishing operations."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ManifestItem(BaseModel):
    """Schema for a single manifest item."""
    
    host: str = Field(..., description="Domain name")
    path: str = Field(..., description="URL path")
    resource_type: str = Field(..., description="Resource type")
    resource_id: str = Field(..., description="Resource ID")
    version: int = Field(..., description="Version number")
    
    def to_compact_format(self) -> list:
        """Convert to compact format for manifest."""
        return [self.host, self.path, self.resource_type, self.resource_id, self.version]


class ManifestResponse(BaseModel):
    """Schema for manifest response."""
    
    generated_at: datetime = Field(..., description="When the manifest was generated")
    count: int = Field(..., description="Number of items in manifest")
    items: list[list] = Field(..., description="Compact manifest items")
    s3_url: Optional[str] = Field(None, description="S3 URL if uploaded")
    etag: Optional[str] = Field(None, description="ETag if uploaded")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "generated_at": "2025-08-22T10:05:00Z",
                "count": 1234,
                "items": [
                    ["slotifyme.com", "/barbershop-a", "tenant", "ten_123", 5],
                    ["slotifyme.com", "/barbershop-a/downtown", "location", "loc_456", 3]
                ],
                "s3_url": "https://s3.amazonaws.com/bucket/router/manifest.json",
                "etag": "abc123"
            }
        }
    )
