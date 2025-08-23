"""Plan model for defining subscription plans."""

from datetime import datetime
from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.sql import func

from app.db import Base


class Plan(Base):
    """Plan model for subscription plans."""
    
    __tablename__ = "plans"
    
    code = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    limits_json = Column(JSON, nullable=False, default=dict)
    features_json = Column(JSON, nullable=False, default=dict)
    overage_policy_json = Column(JSON, nullable=False, default=dict)
    pricing_ref = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    def __repr__(self):
        return f"<Plan(code='{self.code}', name='{self.name}')>"
