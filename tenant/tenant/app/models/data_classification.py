"""Data classification model for controlling field visibility."""

from typing import Optional
from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from tenant.app.db import Base
import enum


class DataClassification(str, enum.Enum):
    """Data classification enum."""
    PUBLIC = "public"
    PRIVATE = "private"
    SENSITIVE = "sensitive"


class DataClassificationRule(Base):
    """Data classification rules for field visibility."""
    
    __tablename__ = "data_classification"
    
    table_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    column_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    classification: Mapped[DataClassification] = mapped_column(
        String(20), 
        nullable=False
    )
    visibility_controlled: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<DataClassificationRule(table={self.table_name}, column={self.column_name}, classification={self.classification})>"
