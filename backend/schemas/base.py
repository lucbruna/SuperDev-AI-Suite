from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    model_config = {"from_attributes": True}


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool


class ApiResponse(BaseModel):
    success: bool = True
    data: Any = None
    message: str | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: dict[str, Any] | None = None
