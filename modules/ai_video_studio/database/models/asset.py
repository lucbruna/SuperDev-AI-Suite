"""Asset model — files (video, audio, image, font, etc.) attached to a project."""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import Float, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class Asset(Base, TimestampMixin):
    __tablename__ = "avs_assets"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    project_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("avs_video_projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    # video, audio, image, subtitle, font, music, sound_effect, voice_over, avatar, template
    mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    codec: Mapped[str | None] = mapped_column(String(32), nullable=True)
    fps: Mapped[float | None] = mapped_column(Float, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    tags: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    extra_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    project: Mapped[VideoProject] = relationship("VideoProject", back_populates="assets")

    __table_args__ = (
        Index("idx_asset_project_type", "project_id", "asset_type"),
    )

    def __repr__(self) -> str:
        return f"<Asset {self.name!r} ({self.asset_type})>"

    @property
    def size_mb(self) -> float:
        return self.file_size_bytes / (1024 * 1024) if self.file_size_bytes else 0.0

    @property
    def is_video(self) -> bool:
        return self.asset_type == "video"

    @property
    def is_audio(self) -> bool:
        return self.asset_type in ("audio", "music", "sound_effect", "voice_over")
