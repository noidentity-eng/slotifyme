"""Pagination utilities for list endpoints."""

from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


def calculate_pagination_info(total: int, page: int, page_size: int) -> dict:
    """Calculate pagination metadata."""
    total_pages = (total + page_size - 1) // page_size
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
    }


def apply_pagination(query, pagination: PaginationParams):
    """Apply pagination to a SQLAlchemy query."""
    offset = (pagination.page - 1) * pagination.page_size
    return query.offset(offset).limit(pagination.page_size)
