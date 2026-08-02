"""VideoProject model — the top-level container for all video work."""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import Float, Index, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class VideoProject(Base, TimestampMixin):
    __tablename__ = "avs_video_projects"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False, index=True)
    # draft, in_progress, rendering, completed, published, archived

    # Video settings
    resolution: Mapped[str] = mapped_column(String(20), default="1920x1080")
    aspect_ratio: Mapped[str] = mapped_column(String(10), default="16:9")
    frame_rate: Mapped[int] = mapped_column(Integer, default=30)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    video_codec: Mapped[str] = mapped_column(String(32), default="libx264")
    audio_codec: Mapped[str] = mapped_column(String(32), default="aac")
    container: Mapped[str] = mapped_column(String(16), default="mp4")

    # AI settings
    ai_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_style: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ai_language: Mapped[str] = mapped_column(String(10), default="en")

    # Metadata
    tags: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    output_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    extra_metadata: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    # Relationships
    scenes: Mapped[list[Scene]] = relationship(
        "Scene", back_populates="project", cascade="all, delete-orphan",
        order_by="Scene.order_index"
    )
    timelines: Mapped[list[Timeline]] = relationship(
        "Timeline", back_populates="project", cascade="all, delete-orphan"
    )
    assets: Mapped[list[Asset]] = relationship(
        "Asset", back_populates="project", cascade="all, delete-orphan"
    )
    render_jobs: Mapped[list[RenderJob]] = relationship(
        "RenderJob", back_populates="project", cascade="all, delete-orphan"
    )
    audio_tracks: Mapped[list[AudioTrack]] = relationship(
        "AudioTrack", back_populates="project", cascade="all, delete-orphan"
    )
    subtitles: Mapped[list[Subtitle]] = relationship(
        "Subtitle", back_populates="project", cascade="all, delete-orphan"
    )
    exports: Mapped[list[ExportHistory]] = relationship(
        "ExportHistory", back_populates="project", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_project_owner_status", "owner_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<VideoProject {self.name!r} ({self.status})>"

    @property
    def is_renderable(self) -> bool:
        return self.status in ("draft", "in_progress") and len(self.scenes) > 0

    @property
    def total_scene_duration(self) -> float:
        return sum(s.duration for s in self.scenes) if self.scenes else 0.0
