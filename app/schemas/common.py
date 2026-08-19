from pydantic import BaseModel
from typing import Any, Optional, List


class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    skip: int
    limit: int
