"""Tenant user model for linking users to tenants."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from tenant.app.db import Base
import enum


class UserRole(str, enum.Enum):
    """User role enum."""
    OWNER = "owner"
    STAFF = "staff"
    STYLIST = "stylist"


class TenantUser(Base):
    """Tenant user model for linking users to tenants."""
    
    __tablename__ = "tenant_users"
    
    tenant_id: Mapped[str] = mapped_column(
        String(26), 
        ForeignKey("tenants.id", ondelete="CASCADE"), 
        primary_key=True
    )
    user_id: Mapped[str] = mapped_column(String(26), primary_key=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow, 
        nullable=False
    )
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="users")
    
    def __repr__(self) -> str:
        return f"<TenantUser(tenant_id={self.tenant_id}, user_id={self.user_id}, role={self.role})>"
