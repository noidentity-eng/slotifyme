"""OveragePriceRefs model for tenant overage pricing references."""

from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func

from app.db import Base


class OveragePriceRefs(Base):
    """OveragePriceRefs model for tenant overage pricing references."""
    
    __tablename__ = "overage_price_refs"
    
    tenant_id = Column(String, primary_key=True, index=True)
    per_stylist_ref = Column(String, nullable=True)
    per_location_ref = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    def __repr__(self):
        return f"<OveragePriceRefs(tenant_id='{self.tenant_id}', per_stylist_ref='{self.per_stylist_ref}', per_location_ref='{self.per_location_ref}')>"
