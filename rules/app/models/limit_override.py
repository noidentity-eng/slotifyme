"""TenantLimitOverride model for tenant limit overrides."""

from datetime import datetime
from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.sql import func
import uuid

from app.db import Base


class TenantLimitOverride(Base):
    """TenantLimitOverride model for tenant limit overrides."""
    
    __tablename__ = "tenant_limit_overrides"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    key = Column(String, nullable=False)
    value_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    def __repr__(self):
        return f"<TenantLimitOverride(id='{self.id}', tenant_id='{self.tenant_id}', key='{self.key}')>"
