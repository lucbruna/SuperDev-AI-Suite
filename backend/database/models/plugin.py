from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Enum as SAEnum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin
import sqlalchemy as sa


class Plugin(Base, TimestampMixin):
    __tablename__ = "plugins"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))
    project_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    manifest: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(SAEnum('installed', 'enabled', 'disabled', 'error', name='plugin_status'), server_default='installed', nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, server_default='{}', nullable=False)
    installed_by: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="plugins")
    installed_by_user: Mapped["User"] = relationship("User", back_populates="installed_plugins", foreign_keys=[installed_by])