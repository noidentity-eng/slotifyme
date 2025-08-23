"""Addon model for defining addon features."""

from datetime import datetime
from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.sql import func

from app.db import Base


class Addon(Base):
    """Addon model for addon features."""
    
    __tablename__ = "addons"
    
    code = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    meta_json = Column(JSON, nullable=False, default=dict)
    effect_json = Column(JSON, nullable=False, default=dict)
    pricing_ref = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    def __repr__(self):
        return f"<Addon(code='{self.code}', name='{self.name}')>"
