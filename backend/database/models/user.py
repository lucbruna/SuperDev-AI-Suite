from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true', nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false', nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false', nullable=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false', nullable=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    owned_projects: Mapped[list[Project]] = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")
    organization_memberships: Mapped[list[OrganizationMember]] = relationship("OrganizationMember", back_populates="user", foreign_keys="OrganizationMember.user_id")
    invited_members: Mapped[list[OrganizationMember]] = relationship("OrganizationMember", back_populates="inviter", foreign_keys="OrganizationMember.invited_by")
    project_memberships: Mapped[list[ProjectMember]] = relationship("ProjectMember", back_populates="user", cascade="all, delete-orphan")
    created_workflows: Mapped[list[Workflow]] = relationship("Workflow", back_populates="creator", foreign_keys="Workflow.created_by")
    created_agents: Mapped[list[Agent]] = relationship("Agent", back_populates="created_by_user", foreign_keys="Agent.created_by")
    created_knowledge_bases: Mapped[list[KnowledgeBase]] = relationship("KnowledgeBase", back_populates="creator", foreign_keys="KnowledgeBase.created_by")
    created_knowledge_entries: Mapped[list[KnowledgeEntry]] = relationship("KnowledgeEntry", back_populates="creator", foreign_keys="KnowledgeEntry.created_by")
    installed_plugins: Mapped[list[Plugin]] = relationship("Plugin", back_populates="installed_by_user", foreign_keys="Plugin.installed_by")
    created_providers: Mapped[list[Provider]] = relationship("Provider", back_populates="creator", foreign_keys="Provider.created_by")
    created_api_keys: Mapped[list[APIKey]] = relationship("APIKey", back_populates="creator", foreign_keys="APIKey.created_by")
    audit_logs: Mapped[list[AuditLog]] = relationship("AuditLog", back_populates="user", foreign_keys="AuditLog.user_id")
    workflow_runs: Mapped[list[WorkflowRun]] = relationship("WorkflowRun", back_populates="triggered_by_user", foreign_keys="WorkflowRun.triggered_by")
    notifications: Mapped[list[Notification]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    roles: Mapped[list[UserRole]] = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
