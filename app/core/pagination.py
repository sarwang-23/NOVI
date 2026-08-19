"""
Shared pagination utility for all NOVI list endpoints.
Usage:
    from app.core.pagination import paginate
    result = paginate(query, page, page_size)
"""
from fastapi import Query
from typing import TypeVar, Generic, List, Any
from sqlalchemy.orm import Query as SAQuery

T = TypeVar("T")


def paginate(query: SAQuery, page: int, page_size: int) -> dict:
    """
    Apply pagination to a SQLAlchemy query and return a standardized
    pagination envelope.

    Args:
        query: Filtered SQLAlchemy query (before offset/limit).
        page: Current page number (1-indexed).
        page_size: Number of items per page.

    Returns:
        dict with keys: total, page, page_size, total_pages, items.
    """
    total = query.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": items,
    }


# Reusable FastAPI query params for pagination — use with Depends()
class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number (1-indexed)"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.page_size = page_size
