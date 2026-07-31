from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))
    organization_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    visibility: Mapped[str] = mapped_column(SAEnum('private', 'team', 'public', name='project_visibility'), server_default='private', nullable=False)
    settings: Mapped[dict] = mapped_column(JSONB, server_default='{}', nullable=False)
    repository_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    repository_branch: Mapped[str | None] = mapped_column(String(100), nullable=True)

    organization: Mapped[Organization] = relationship("Organization", back_populates="projects")
    owner: Mapped[User] = relationship("User", back_populates="owned_projects", foreign_keys=[owner_id])
    members: Mapped[list[ProjectMember]] = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    workflows: Mapped[list[Workflow]] = relationship("Workflow", back_populates="project", cascade="all, delete-orphan")
    agents: Mapped[list[Agent]] = relationship("Agent", back_populates="project", cascade="all, delete-orphan")
    providers: Mapped[list[Provider]] = relationship("Provider", back_populates="project", cascade="all, delete-orphan")
    plugins: Mapped[list[Plugin]] = relationship("Plugin", back_populates="project", cascade="all, delete-orphan")
    knowledge_bases: Mapped[list[KnowledgeBase]] = relationship("KnowledgeBase", back_populates="project", cascade="all, delete-orphan")


class ProjectMember(Base, TimestampMixin):
    __tablename__ = "project_members"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))
    project_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(SAEnum('owner', 'admin', 'member', 'viewer', name='user_role'), server_default='member', nullable=False)

    project: Mapped[Project] = relationship("Project", back_populates="members")
    user: Mapped[User] = relationship("User", back_populates="project_memberships")
