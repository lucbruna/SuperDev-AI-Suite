from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Text, Boolean, Enum as SAEnum, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin
import sqlalchemy as sa


class Workflow(Base, TimestampMixin):
    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))
    project_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    definition: Mapped[dict] = mapped_column(JSONB, nullable=False)
    version: Mapped[int] = mapped_column(Integer, server_default='1', nullable=False)
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), server_default='{}', nullable=False)
    is_template: Mapped[bool] = mapped_column(Boolean, server_default='false', nullable=False)
    created_by: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="workflows")
    creator: Mapped["User"] = relationship("User", back_populates="created_workflows", foreign_keys=[created_by])
    runs: Mapped[List["WorkflowRun"]] = relationship("WorkflowRun", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))
    workflow_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(SAEnum('pending', 'running', 'completed', 'failed', 'cancelled', name='workflow_status'), server_default='pending', nullable=False)
    trigger: Mapped[str] = mapped_column(String(50), nullable=False)
    triggered_by: Mapped[Optional[str]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    variables: Mapped[dict] = mapped_column(JSONB, server_default='{}', nullable=False)
    result: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)

    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="runs")
    triggered_by_user: Mapped[Optional["User"]] = relationship("User", back_populates="workflow_runs", foreign_keys=[triggered_by])
    steps: Mapped[List["WorkflowStep"]] = relationship("WorkflowStep", back_populates="run", cascade="all, delete-orphan")
    agent_executions: Mapped[List["AgentExecution"]] = relationship("AgentExecution", back_populates="run", foreign_keys="AgentExecution.run_id")


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))
    run_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    step_type: Mapped[str] = mapped_column(String(50), nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(SAEnum('pending', 'running', 'completed', 'failed', 'cancelled', name='workflow_status'), server_default='pending', nullable=False)
    input: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    output: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retries: Mapped[int] = mapped_column(Integer, server_default='0', nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)

    run: Mapped["WorkflowRun"] = relationship("WorkflowRun", back_populates="steps")