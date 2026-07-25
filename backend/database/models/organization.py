from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Text, Boolean, Enum as SAEnum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin
import sqlalchemy as sa


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    plan: Mapped[str] = mapped_column(SAEnum('free', 'pro', 'enterprise', name='organization_plan'), server_default='free', nullable=False)
    settings: Mapped[dict] = mapped_column(JSONB, server_default='{}', nullable=False)

    members: Mapped[List["OrganizationMember"]] = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="organization", cascade="all, delete-orphan")
    api_keys: Mapped[List["APIKey"]] = relationship("APIKey", back_populates="organization", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="organization", cascade="all, delete-orphan")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="organization", cascade="all, delete-orphan")


class OrganizationMember(Base, TimestampMixin):
    __tablename__ = "organization_members"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))
    organization_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(SAEnum('owner', 'admin', 'member', 'viewer', name='user_role'), server_default='member', nullable=False)
    invited_by: Mapped[Optional[str]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    invited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    joined_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="organization_memberships", foreign_keys=[user_id])
    inviter: Mapped[Optional["User"]] = relationship("User", foreign_keys=[invited_by])