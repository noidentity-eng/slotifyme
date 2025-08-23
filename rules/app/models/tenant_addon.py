"""TenantAddon model for tenant addon assignments."""

from datetime import datetime
from sqlalchemy import Column, String, JSON, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db import Base


class TenantAddon(Base):
    """TenantAddon model for tenant addon assignments."""
    
    __tablename__ = "tenant_addons"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    addon_code = Column(String, ForeignKey("addons.code"), nullable=False)
    qty = Column(Integer, nullable=False, default=1)
    meta_json = Column(JSON, nullable=False, default=dict)
    pricing_ref = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationship
    addon = relationship("Addon", backref="tenant_addons")
    
    def __repr__(self):
        return f"<TenantAddon(id='{self.id}', tenant_id='{self.tenant_id}', addon_code='{self.addon_code}', qty={self.qty})>"
