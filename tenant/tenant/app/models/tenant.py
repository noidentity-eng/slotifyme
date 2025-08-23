"""Tenant model."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, DateTime, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from tenant.app.db import Base
import enum


class TenantStatus(str, enum.Enum):
    """Tenant status enum."""
    ACTIVE = "active"
    DISABLED = "disabled"
    SUSPENDED = "suspended"


class Tenant(Base):
    """Tenant model."""
    
    __tablename__ = "tenants"
    
    id: Mapped[str] = mapped_column(String(26), primary_key=True)  # ULID
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[TenantStatus] = mapped_column(
        Enum(TenantStatus), 
        default=TenantStatus.ACTIVE, 
        nullable=False
    )
    theme_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(Text, nullable=True)
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
    locations: Mapped[List["Location"]] = relationship("Location", back_populates="tenant", cascade="all, delete-orphan")
    users: Mapped[List["TenantUser"]] = relationship("TenantUser", back_populates="tenant", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, slug={self.slug}, name={self.name})>"
