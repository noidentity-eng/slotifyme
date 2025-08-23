"""SQLAlchemy model for slug history audit trail."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class SlugHistory(Base):
    """Model for slug mapping history audit trail."""
    
    __tablename__ = "slug_history"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # Foreign key to slug_map
    slug_map_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("slug_map.id"), nullable=False, index=True
    )
    
    # Audit fields
    old_values_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    new_values_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    actor: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Relationship
    slug_map = relationship("SlugMap", back_populates="history")
    
    def __repr__(self) -> str:
        return f"<SlugHistory(id={self.id}, slug_map_id={self.slug_map_id})>"
