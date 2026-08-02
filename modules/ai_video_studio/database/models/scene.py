"""Scene model — individual segments within a video project."""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class Scene(Base, TimestampMixin):
    __tablename__ = "avs_scenes"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    project_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("avs_video_projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    scene_type: Mapped[str] = mapped_column(String(32), default="content")
    # intro, content, transition, outro, title_card, b_roll, highlight, credits

    # Timing
    start_time: Mapped[float] = mapped_column(Float, default=0.0)
    duration: Mapped[float] = mapped_column(Float, default=5.0)
    end_time: Mapped[float] = mapped_column(Float, default=5.0)

    # Content
    script: Mapped[str | None] = mapped_column(Text, nullable=True)
    visual_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    voiceover_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Visual settings
    background_color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    transition_in: Mapped[str] = mapped_column(String(32), default="cut")
    transition_out: Mapped[str] = mapped_column(String(32), default="cut")
    transition_duration: Mapped[float] = mapped_column(Float, default=0.5)

    # AI generation state
    generation_status: Mapped[str] = mapped_column(String(32), default="pending")
    # pending, generating, ready, failed
    generated_video_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    generated_image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Extra
    extra_data: Mapped[dict | None] = mapped_column("extra_data", JSON, nullable=True)

    # Relationships
    project: Mapped[VideoProject] = relationship("VideoProject", back_populates="scenes")
    audio_tracks: Mapped[list[AudioTrack]] = relationship(
        "AudioTrack", back_populates="scene", cascade="all, delete-orphan"
    )
    subtitles: Mapped[list[Subtitle]] = relationship(
        "Subtitle", back_populates="scene", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_scene_project_order", "project_id", "order_index"),
    )

    def __repr__(self) -> str:
        return f"<Scene {self.name!r} order={self.order_index}>"

    def recalc_end(self) -> None:
        self.end_time = self.start_time + self.duration
