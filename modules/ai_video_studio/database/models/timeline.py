"""Timeline model — tracks the master edit sequence for a project."""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class Timeline(Base, TimestampMixin):
    __tablename__ = "avs_timelines"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    project_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("avs_video_projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), default="Main Timeline")
    track_type: Mapped[str] = mapped_column(String(32), default="video")
    # video, audio, subtitle, overlay, effect

    order_index: Mapped[int] = mapped_column(Integer, default=0)
    is_muted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    volume: Mapped[float] = mapped_column(Float, default=1.0)

    # Track the sequence of clips on this track (JSON array of clip references)
    clips: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # clips = [{"scene_id": "...", "start": 0.0, "end": 5.0, "trim_start": 0.0, "trim_end": 0.0}]

    # Project-wide timing
    total_duration: Mapped[float] = mapped_column(Float, default=0.0)
    fps: Mapped[int] = mapped_column(Integer, default=30)

    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    project: Mapped[VideoProject] = relationship("VideoProject", back_populates="timelines")

    __table_args__ = (
        Index("idx_timeline_project_type", "project_id", "track_type"),
    )

    def __repr__(self) -> str:
        return f"<Timeline {self.name!r} ({self.track_type})>"

    def add_clip(self, scene_id: str, start: float, end: float) -> None:
        if self.clips is None:
            self.clips = []
        self.clips.append({
            "scene_id": scene_id,
            "start": start,
            "end": end,
            "trim_start": 0.0,
            "trim_end": 0.0,
        })
        self.total_duration = max(self.total_duration, end)

    def remove_clip(self, scene_id: str) -> None:
        if self.clips:
            self.clips = [c for c in self.clips if c.get("scene_id") != scene_id]
            self.total_duration = max((c["end"] for c in self.clips), default=0.0)
