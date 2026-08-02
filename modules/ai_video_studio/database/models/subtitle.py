"""Subtitle model — captions/subtitles attached to scenes."""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import Float, ForeignKey, Index, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class Subtitle(Base, TimestampMixin):
    __tablename__ = "avs_subtitles"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    project_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("avs_video_projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scene_id: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("avs_scenes.id", ondelete="SET NULL"), nullable=True, index=True
    )

    text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en")
    start_time: Mapped[float] = mapped_column(Float, default=0.0)
    end_time: Mapped[float] = mapped_column(Float, default=0.0)
    duration: Mapped[float] = mapped_column(Float, default=0.0)

    # Style
    font_name: Mapped[str] = mapped_column(String(64), default="Arial")
    font_size: Mapped[int] = mapped_column(default=24)
    font_color: Mapped[str] = mapped_column(String(7), default="#FFFFFF")
    background_color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    position_x: Mapped[float] = mapped_column(Float, default=0.5)
    position_y: Mapped[float] = mapped_column(Float, default=0.9)
    alignment: Mapped[str] = mapped_column(String(8), default="center")
    border_width: Mapped[int] = mapped_column(default=2)

    # Translation
    is_translation: Mapped[bool] = mapped_column(default=False)
    original_subtitle_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    project: Mapped[VideoProject] = relationship("VideoProject", back_populates="subtitles")
    scene: Mapped[Scene | None] = relationship("Scene", back_populates="subtitles")

    __table_args__ = (
        Index("idx_subtitle_project_lang", "project_id", "language"),
    )

    def __repr__(self) -> str:
        return f"<Subtitle {self.text[:30]!r} ({self.language})>"

    @property
    def word_count(self) -> int:
        return len(self.text.split()) if self.text else 0
