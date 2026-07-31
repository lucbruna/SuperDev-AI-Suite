from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class KnowledgeBase(Base, TimestampMixin):
    __tablename__ = "knowledge_bases"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    project_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(50), server_default="documentation", nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(100), server_default="all-MiniLM-L6-v2", nullable=False)
    embedding_dimension: Mapped[int] = mapped_column(Integer, server_default="384", nullable=False)
    chunk_size: Mapped[int] = mapped_column(Integer, server_default="1000", nullable=False)
    chunk_overlap: Mapped[int] = mapped_column(Integer, server_default="200", nullable=False)
    settings: Mapped[dict] = mapped_column(JSONB, server_default="{}", nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    created_by: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    project: Mapped[Project] = relationship("Project", back_populates="knowledge_bases")
    creator: Mapped[User] = relationship("User", back_populates="created_knowledge_bases", foreign_keys=[created_by])
    entries: Mapped[list[KnowledgeEntry]] = relationship(
        "KnowledgeEntry", back_populates="knowledge_base", cascade="all, delete-orphan"
    )


class KnowledgeEntry(Base, TimestampMixin):
    __tablename__ = "knowledge_entries"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    knowledge_base_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), server_default="{}", nullable=False)
    extra_metadata: Mapped[dict] = mapped_column(JSONB, server_default="{}", nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    created_by: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    knowledge_base: Mapped[KnowledgeBase] = relationship("KnowledgeBase", back_populates="entries")
    creator: Mapped[User] = relationship("User", back_populates="created_knowledge_entries", foreign_keys=[created_by])
    chunks: Mapped[list[KnowledgeChunk]] = relationship(
        "KnowledgeChunk", back_populates="entry", cascade="all, delete-orphan"
    )


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    entry_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("knowledge_entries.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    extra_metadata: Mapped[dict] = mapped_column(JSONB, server_default="{}", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
    )

    entry: Mapped[KnowledgeEntry] = relationship("KnowledgeEntry", back_populates="chunks")
