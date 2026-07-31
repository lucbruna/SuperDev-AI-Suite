from __future__ import annotations

import os
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

# Use schema only for PostgreSQL (not SQLite in tests)
_DB_URL = os.getenv("DATABASE_URL", "")
_DB_SCHEMA = "superdev" if "postgresql" in _DB_URL else None


class Base(DeclarativeBase):
    metadata = MetaData(schema=_DB_SCHEMA)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class UUIDMixin:
    @declared_attr
    def id(self) -> Mapped[UUID]:
        return mapped_column(
            PG_UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        )


# Import needed for TimestampMixin
import sqlalchemy as sa
