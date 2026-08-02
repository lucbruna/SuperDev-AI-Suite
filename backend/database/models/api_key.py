from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin

# Shared key-format constant: the 24-char lookup prefix (``sk_`` + 21 hex). It
# MUST stay in sync with ``raw[:API_KEY_PREFIX_LENGTH]`` generation in
# backend/api/v1/api_keys.py and the ``APIKeyAuth`` lookup slice in
# backend/auth/manager.py — drifting these two caused every API key to be
# unfindable (finding 2f29e692, HIGH). String(20) previously truncated it.
API_KEY_PREFIX_LENGTH = 24


class APIKey(Base, TimestampMixin):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    organization_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # Must hold API_KEY_PREFIX_LENGTH (24) chars; String(20) truncated it and
    # made every created key unfindable.
    key_prefix: Mapped[str] = mapped_column(String(32), nullable=False)
    scopes: Mapped[list[str]] = mapped_column(ARRAY(String), server_default="{}", nullable=False)
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean(), server_default=sa.text("true"), nullable=False, index=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    organization: Mapped[Organization] = relationship("Organization", back_populates="api_keys")
    creator: Mapped[User] = relationship("User", back_populates="created_api_keys", foreign_keys=[created_by])
