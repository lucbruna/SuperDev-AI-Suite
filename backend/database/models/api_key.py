from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Enum as SAEnum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin
import sqlalchemy as sa


class APIKey(Base, TimestampMixin):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))
    organization_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(20), nullable=False)
    scopes: Mapped[List[str]] = mapped_column(ARRAY(String), server_default='{}', nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="api_keys")
    creator: Mapped["User"] = relationship("User", back_populates="created_api_keys", foreign_keys=[created_by])