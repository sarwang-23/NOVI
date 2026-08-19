"""
Standardized error response helpers for NOVI backend.

All endpoints should raise errors via these helpers so the frontend
always receives a consistent error shape:
    {
        "error": "<machine-readable code>",
        "message": "<human-readable message>",
        "detail": <optional extra context>
    }
"""
from fastapi import HTTPException
from typing import Any, Optional


def not_found(resource: str, identifier: Any = None) -> HTTPException:
    msg = f"{resource} not found"
    if identifier is not None:
        msg = f"{resource} with id '{identifier}' not found"
    return HTTPException(
        status_code=404,
        detail={"error": "NOT_FOUND", "message": msg},
    )


def forbidden(reason: str = "You do not have permission to perform this action") -> HTTPException:
    return HTTPException(
        status_code=403,
        detail={"error": "FORBIDDEN", "message": reason},
    )


def unauthorized(reason: str = "Authentication required") -> HTTPException:
    return HTTPException(
        status_code=401,
        detail={"error": "UNAUTHORIZED", "message": reason},
    )


def bad_request(reason: str, field: Optional[str] = None) -> HTTPException:
    detail: dict = {"error": "BAD_REQUEST", "message": reason}
    if field:
        detail["field"] = field
    return HTTPException(status_code=400, detail=detail)


def conflict(reason: str) -> HTTPException:
    return HTTPException(
        status_code=409,
        detail={"error": "CONFLICT", "message": reason},
    )


def unprocessable(reason: str) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={"error": "UNPROCESSABLE", "message": reason},
    )


def server_error(reason: str = "An unexpected error occurred") -> HTTPException:
    return HTTPException(
        status_code=500,
        detail={"error": "INTERNAL_SERVER_ERROR", "message": reason},
    )
