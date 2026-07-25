from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Text, Boolean, Enum as SAEnum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin
import sqlalchemy as sa


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default='true', nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, server_default='false', nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, server_default='false', nullable=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, server_default='false', nullable=False)
    mfa_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    owned_projects: Mapped[List["Project"]] = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")
    organization_memberships: Mapped[List["OrganizationMember"]] = relationship("OrganizationMember", back_populates="user", foreign_keys="OrganizationMember.user_id")
    invited_members: Mapped[List["OrganizationMember"]] = relationship("OrganizationMember", back_populates="inviter", foreign_keys="OrganizationMember.invited_by")
    project_memberships: Mapped[List["ProjectMember"]] = relationship("ProjectMember", back_populates="user", cascade="all, delete-orphan")
    created_workflows: Mapped[List["Workflow"]] = relationship("Workflow", back_populates="created_by", foreign_keys="Workflow.created_by")
    created_agents: Mapped[List["Agent"]] = relationship("Agent", back_populates="created_by", foreign_keys="Agent.created_by")
    created_knowledge_bases: Mapped[List["KnowledgeBase"]] = relationship("KnowledgeBase", back_populates="created_by", foreign_keys="KnowledgeBase.created_by")
    installed_plugins: Mapped[List["Plugin"]] = relationship("Plugin", back_populates="installed_by", foreign_keys="Plugin.installed_by")
    created_providers: Mapped[List["Provider"]] = relationship("Provider", back_populates="created_by", foreign_keys="Provider.created_by")
    created_api_keys: Mapped[List["APIKey"]] = relationship("APIKey", back_populates="created_by", foreign_keys="APIKey.created_by")
    agent_executions: Mapped[List["AgentExecution"]] = relationship("AgentExecution", back_populates="user", foreign_keys="AgentExecution.user_id")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user", foreign_keys="AuditLog.user_id")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")