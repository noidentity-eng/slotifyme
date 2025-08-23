"""Location model."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, Text, Enum, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from tenant.app.db import Base
import enum


class LocationStatus(str, enum.Enum):
    """Location status enum."""
    ACTIVE = "active"
    DISABLED = "disabled"


class Location(Base):
    """Location model."""
    
    __tablename__ = "locations"
    
    id: Mapped[str] = mapped_column(String(26), primary_key=True)  # ULID
    tenant_id: Mapped[str] = mapped_column(
        String(26), 
        ForeignKey("tenants.id", ondelete="CASCADE"), 
        nullable=False
    )
    slug: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False)
    phone_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[LocationStatus] = mapped_column(
        Enum(LocationStatus), 
        default=LocationStatus.ACTIVE, 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow, 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="locations")
    
    def __repr__(self) -> str:
        return f"<Location(id={self.id}, slug={self.slug}, name={self.name})>"
