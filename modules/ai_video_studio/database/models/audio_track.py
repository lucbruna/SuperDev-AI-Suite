"""AudioTrack model — audio layers (voice, music, SFX) on scenes."""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import Boolean, Float, ForeignKey, Index, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class AudioTrack(Base, TimestampMixin):
    __tablename__ = "avs_audio_tracks"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    project_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("avs_video_projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scene_id: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("avs_scenes.id", ondelete="SET NULL"), nullable=True, index=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    track_type: Mapped[str] = mapped_column(String(32), default="voice_over")
    # voice_over, music, sound_effect, ambient, narration
    file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    duration: Mapped[float] = mapped_column(Float, default=0.0)
    start_time: Mapped[float] = mapped_column(Float, default=0.0)
    volume: Mapped[float] = mapped_column(Float, default=1.0)
    fade_in: Mapped[float] = mapped_column(Float, default=0.0)
    fade_out: Mapped[float] = mapped_column(Float, default=0.0)
    is_muted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_loop: Mapped[bool] = mapped_column(Boolean, default=False)

    # Voice synthesis settings
    voice_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    voice_speed: Mapped[float] = mapped_column(Float, default=1.0)
    voice_pitch: Mapped[float] = mapped_column(Float, default=1.0)
    emotion: Mapped[str | None] = mapped_column(String(32), nullable=True)

    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    project: Mapped[VideoProject] = relationship("VideoProject", back_populates="audio_tracks")
    scene: Mapped[Scene | None] = relationship("Scene", back_populates="audio_tracks")

    __table_args__ = (
        Index("idx_audio_project_type", "project_id", "track_type"),
    )

    def __repr__(self) -> str:
        return f"<AudioTrack {self.name!r} ({self.track_type}) vol={self.volume:.2f}>"
