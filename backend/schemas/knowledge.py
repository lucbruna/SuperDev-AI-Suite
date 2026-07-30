from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from backend.schemas.base import BaseSchema


# ── Knowledge Base Schemas ─────────────────────────────────────


class KnowledgeBaseCreate(BaseModel):
    """Request to create a new knowledge base."""

    project_id: str = Field(..., description="Project UUID")
    name: str = Field(..., min_length=1, max_length=255, description="Knowledge base name")
    description: str | None = Field(None, description="Knowledge base description")
    type: str = Field("documentation", description="KB type: documentation, codebase, faq, etc.")
    embedding_model: str = Field("all-MiniLM-L6-v2", description="Embedding model identifier")
    embedding_dimension: int = Field(384, description="Embedding vector dimension")
    chunk_size: int = Field(1000, ge=100, le=10000, description="Text chunk size in tokens")
    chunk_overlap: int = Field(200, ge=0, le=2000, description="Overlap between chunks")
    is_public: bool = Field(False, description="Whether publicly accessible")


class KnowledgeBaseResponse(BaseSchema):
    """Knowledge base response."""

    id: str = Field(..., description="Knowledge base UUID")
    project_id: str = Field(..., description="Project UUID")
    name: str = Field(..., description="Knowledge base name")
    description: str | None = Field(None, description="Description")
    type: str = Field(..., description="KB type")
    embedding_model: str = Field(..., description="Embedding model")
    embedding_dimension: int = Field(..., description="Embedding dimension")
    chunk_size: int = Field(..., description="Chunk size")
    chunk_overlap: int = Field(..., description="Chunk overlap")
    is_public: bool = Field(False, description="Public flag")
    created_by: str = Field(..., description="Creator UUID")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")


# ── Knowledge Entry Schemas ────────────────────────────────────


class KnowledgeEntryCreate(BaseModel):
    """Request to create a knowledge entry."""

    knowledge_base_id: str = Field(..., description="Knowledge base UUID")
    title: str = Field(..., min_length=1, max_length=500, description="Entry title")
    content: str = Field(..., min_length=1, description="Entry content text")
    source_url: str | None = Field(None, max_length=2000, description="Source URL")
    source_type: str | None = Field(None, max_length=50, description="Source type (url, file, etc.)")
    language: str | None = Field(None, max_length=50, description="Content language")
    tags: list[str] = Field(default_factory=list, description="Entry tags")


class KnowledgeEntryResponse(BaseSchema):
    """Knowledge entry response."""

    id: str = Field(..., description="Entry UUID")
    knowledge_base_id: str = Field(..., description="Knowledge base UUID")
    title: str = Field(..., description="Entry title")
    content: str = Field(..., description="Entry content")
    source_url: str | None = Field(None, description="Source URL")
    source_type: str | None = Field(None, description="Source type")
    language: str | None = Field(None, description="Content language")
    tags: list[str] = Field(default_factory=list, description="Entry tags")
    token_count: int = Field(0, description="Token count")
    created_by: str = Field(..., description="Creator UUID")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")


# ── Knowledge Chunk Schemas ────────────────────────────────────


class KnowledgeChunkResponse(BaseSchema):
    """Knowledge chunk response (for vector search results)."""

    id: str = Field(..., description="Chunk UUID")
    entry_id: str = Field(..., description="Entry UUID")
    chunk_index: int = Field(..., description="Chunk sequence number")
    content: str = Field(..., description="Chunk content text")
    token_count: int = Field(0, description="Token count")
    created_at: datetime | None = Field(None, description="Creation timestamp")
