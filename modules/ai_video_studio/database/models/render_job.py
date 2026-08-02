"""RenderJob model — tracks FFmpeg/GPU render tasks."""
from __future__ import annotations

from datetime import datetime, UTC

import sqlalchemy as sa
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class RenderJob(Base, TimestampMixin):
    __tablename__ = "avs_render_jobs"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    project_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("avs_video_projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(32), default="queued", nullable=False, index=True)
    # queued, preprocessing, rendering, encoding, postprocessing, completed, failed, cancelled

    priority: Mapped[int] = mapped_column(Integer, default=1)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    current_step: Mapped[str | None] = mapped_column(String(128), nullable=True)
    total_steps: Mapped[int] = mapped_column(Integer, default=1)
    completed_steps: Mapped[int] = mapped_column(Integer, default=0)

    # Render configuration
    output_format: Mapped[str] = mapped_column(String(16), default="mp4")
    output_resolution: Mapped[str] = mapped_column(String(20), default="1920x1080")
    video_codec: Mapped[str] = mapped_column(String(32), default="libx264")
    audio_codec: Mapped[str] = mapped_column(String(32), default="aac")
    bitrate: Mapped[str | None] = mapped_column(String(20), nullable=True)
    crf: Mapped[int] = mapped_column(Integer, default=23)
    preset: Mapped[str] = mapped_column(String(32), default="medium")

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_duration: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Output
    output_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    output_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Error tracking
    error_message: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)

    # GPU / resources
    use_gpu: Mapped[bool] = mapped_column(default=False)
    gpu_device: Mapped[str | None] = mapped_column(String(16), nullable=True)
    worker_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    project: Mapped[VideoProject] = relationship("VideoProject", back_populates="render_jobs")

    __table_args__ = (
        Index("idx_render_project_status", "project_id", "status"),
        Index("idx_render_priority_status", "priority", "status"),
    )

    def __repr__(self) -> str:
        return f"<RenderJob {self.status!r} progress={self.progress:.1%}>"

    @property
    def is_terminal(self) -> bool:
        return self.status in ("completed", "failed", "cancelled")

    @property
    def elapsed_seconds(self) -> float | None:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def mark_started(self) -> None:
        from datetime import datetime

        self.status = "rendering"
        self.started_at = datetime.now(UTC)

    def mark_completed(self, output_path: str) -> None:
        from datetime import datetime

        self.status = "completed"
        self.progress = 1.0
        self.output_path = output_path
        self.completed_at = datetime.now(UTC)
        self.actual_duration = self.elapsed_seconds

    def mark_failed(self, error: str, code: str | None = None) -> None:
        from datetime import datetime

        self.status = "failed"
        self.error_message = error
        self.error_code = code
        self.completed_at = datetime.now(UTC)

    def increment_progress(self, amount: float = 0.1) -> None:
        self.progress = min(1.0, self.progress + amount)
        self.completed_steps += 1
        if self.completed_steps >= self.total_steps:
            self.progress = 1.0
