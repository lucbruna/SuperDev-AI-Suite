from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Text, Enum as SAEnum, ForeignKey, DateTime, Integer, Numeric, Boolean, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin
import sqlalchemy as sa


class Agent(Base, TimestampMixin):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))
    project_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(SAEnum('planner', 'executor', 'reviewer', 'tester', 'architect', 'researcher', 'security', 'deployment', name='agent_type'), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config: Mapped[dict] = mapped_column(JSONB, server_default='{}', nullable=False)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tools: Mapped[List[str]] = mapped_column(ARRAY(String), server_default='{}', nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default='true', nullable=False)
    created_by: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="agents")
    created_by_user: Mapped["User"] = relationship("User", back_populates="created_agents", foreign_keys=[created_by])
    executions: Mapped[List["AgentExecution"]] = relationship("AgentExecution", back_populates="agent", cascade="all, delete-orphan")


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))
    agent_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    run_id: Mapped[Optional[str]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="SET NULL"), nullable=True)
    task: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[dict] = mapped_column(JSONB, server_default='{}', nullable=False)
    status: Mapped[str] = mapped_column(SAEnum('idle', 'running', 'completed', 'failed', name='agent_status'), server_default='idle', nullable=False)
    result: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, server_default='0', nullable=False)
    cost_usd: Mapped[float] = mapped_column(Numeric(10, 6), server_default='0', nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)

    agent: Mapped["Agent"] = relationship("Agent", back_populates="executions")
    run: Mapped[Optional["WorkflowRun"]] = relationship("WorkflowRun", back_populates="agent_executions")