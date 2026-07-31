from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class Provider(Base, TimestampMixin):
    __tablename__ = "providers"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))
    project_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(SAEnum('openai', 'anthropic', 'gemini', 'ollama', 'openrouter', 'azure', 'cohere', name='provider_type'), nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    models: Mapped[list[str]] = mapped_column(ARRAY(String), server_default='{}', nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, server_default='false', nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default='true', nullable=False)
    priority: Mapped[int] = mapped_column(Integer, server_default='0', nullable=False)
    created_by: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    project: Mapped[Project] = relationship("Project", back_populates="providers")
    creator: Mapped[User] = relationship("User", back_populates="created_providers", foreign_keys=[created_by])
