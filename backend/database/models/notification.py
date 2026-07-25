from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin
import sqlalchemy as sa


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))
    organization_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[dict] = mapped_column(JSONB, server_default='{}', nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, server_default='false', nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="notifications")
    user: Mapped["User"] = relationship("User", back_populates="notifications")