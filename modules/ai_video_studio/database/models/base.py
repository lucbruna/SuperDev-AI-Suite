"""SQLAlchemy declarative base — re-exported from the backend.

AI Video Studio models share the backend's single `Base` so the whole
platform lives under one metadata, one schema, and one Alembic migration
set (see `backend/database/base.py` and `alembic/env.py`).
"""
from __future__ import annotations

from backend.database.base import Base, TimestampMixin

__all__ = ["Base", "TimestampMixin"]
