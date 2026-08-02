"""ExportHistory model — records every export/render completion."""
from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class ExportHistory(Base, TimestampMixin):
    __tablename__ = "avs_export_history"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    project_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("avs_video_projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    render_job_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    status: Mapped[str] = mapped_column(String(32), default="completed", nullable=False)
    output_format: Mapped[str] = mapped_column(String(16), default="mp4")
    output_resolution: Mapped[str] = mapped_column(String(20), default="1920x1080")
    output_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    output_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    duration: Mapped[float] = mapped_column(Float, default=0.0)
    exported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Platform publishing info
    platform: Mapped[str | None] = mapped_column(String(32), nullable=True)
    platform_video_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    platform_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    project: Mapped[VideoProject] = relationship("VideoProject", back_populates="exports")

    __table_args__ = (
        Index("idx_export_project_status", "project_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<ExportHistory {self.output_format!r} {self.status!r}>"

    @property
    def size_mb(self) -> float:
        return self.file_size_bytes / (1024 * 1024) if self.file_size_bytes else 0.0
