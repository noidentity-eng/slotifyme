"""TenantPlan model for tenant plan assignments."""

from datetime import datetime
from sqlalchemy import Column, String, JSON, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db import Base


class TenantPlan(Base):
    """TenantPlan model for tenant plan assignments."""
    
    __tablename__ = "tenant_plans"
    
    tenant_id = Column(String, primary_key=True, index=True)
    plan_code = Column(String, ForeignKey("plans.code"), nullable=False)
    pricing_ref = Column(String, nullable=True)
    meta_json = Column(JSON, nullable=False, default=dict)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationship
    plan = relationship("Plan", backref="tenant_plans")
    
    def __repr__(self):
        return f"<TenantPlan(tenant_id='{self.tenant_id}', plan_code='{self.plan_code}', version={self.version})>"
