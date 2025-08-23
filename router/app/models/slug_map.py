"""SQLAlchemy model for slug mappings."""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class ResourceType(str, enum.Enum):
    """Resource types that can be mapped to slugs."""
    
    TENANT = "tenant"
    LOCATION = "location"
    STYLIST = "stylist"
    SERVICE = "service"


class SlugStatus(str, enum.Enum):
    """Status of slug mappings."""
    
    ACTIVE = "active"
    DRAFT = "draft"
    DELETED = "deleted"


class SlugMap(Base):
    """Model for slug mappings."""
    
    __tablename__ = "slug_map"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # Slug mapping fields
    host: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    resource_type: Mapped[ResourceType] = mapped_column(
        Enum(ResourceType), nullable=False
    )
    resource_id: Mapped[str] = mapped_column(String(100), nullable=False)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    
    # Metadata
    version: Mapped[int] = mapped_column(default=1, nullable=False)
    status: Mapped[SlugStatus] = mapped_column(
        Enum(SlugStatus), default=SlugStatus.ACTIVE, nullable=False, index=True
    )
    canonical_url: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    history = relationship("SlugHistory", back_populates="slug_map", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        # Unique constraint for active mappings
        UniqueConstraint(
            "host", 
            "path", 
            "status",
            name="uq_slug_map_host_path_status",
            deferrable=True,
        ),
        # Check constraint for path format
        CheckConstraint(
            "path ~ '^/[^\\s]*$'",
            name="ck_slug_map_path_format"
        ),
        # Indexes
        Index("ix_slug_map_tenant_status", "tenant_id", "status"),
        Index("ix_slug_map_resource", "resource_type", "resource_id"),
    )
    
    def __repr__(self) -> str:
        return f"<SlugMap(id={self.id}, host={self.host}, path={self.path})>"
