from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class KnowledgeItem:
    """A unit of stored knowledge (memory, document excerpt, decision, experience)."""

    content: str
    kind: str = "text"
    source: str = "manual"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "kind": self.kind,
            "source": self.source,
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
        }


@dataclass
class MemoryRecord:
    """A persisted memory entry with type and importance."""

    content: str
    memory_type: str = "episodic"
    importance: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utcnow)
    last_accessed_at: str = field(default_factory=_utcnow)
    access_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "memory_type": self.memory_type,
            "importance": self.importance,
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
            "last_accessed_at": self.last_accessed_at,
            "access_count": self.access_count,
        }


@dataclass
class DocumentRecord:
    """A stored document with parsed content and versioning."""

    title: str
    content: str
    doc_type: str = "text"
    version: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "content": self.content,
            "doc_type": self.doc_type,
            "version": self.version,
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
        }


@dataclass
class Chunk:
    """A chunk of a document prepared for embedding and indexing."""

    text: str
    document_id: str = ""
    index: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "document_id": self.document_id,
            "index": self.index,
            "metadata": dict(self.metadata),
        }


@dataclass
class Embedding:
    """A vector embedding paired with its source text."""

    vector: list[float]
    text: str = ""
    document_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "vector": list(self.vector),
            "text": self.text,
            "document_id": self.document_id,
            "metadata": dict(self.metadata),
        }


@dataclass
class SearchResult:
    """A single search hit with relevance score."""

    text: str
    score: float
    source: str = "unknown"
    document_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "score": self.score,
            "source": self.source,
            "document_id": self.document_id,
            "metadata": dict(self.metadata),
        }


@dataclass
class RetrievalContext:
    """Context assembled for retrieval-augmented generation."""

    query: str = ""
    results: list[SearchResult] = field(default_factory=list)
    memory_hits: list[str] = field(default_factory=list)

    def context_text(self, limit: int = 0) -> str:
        items = self.results
        if limit > 0:
            items = items[:limit]
        return "\n\n".join(item.text for item in items)


@dataclass
class Entity:
    """An entity in the knowledge graph."""

    name: str
    entity_type: str = "concept"
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "type": self.entity_type, "properties": dict(self.properties)}


@dataclass
class Relation:
    """A typed relation between two graph entities."""

    source: str
    target: str
    relation_type: str = "related_to"
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.relation_type,
            "properties": dict(self.properties),
        }


@dataclass
class KnowledgeGraphRecord:
    """Serializable knowledge graph with entities and relations."""

    entities: list[Entity] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entities": [e.to_dict() for e in self.entities],
            "relations": [r.to_dict() for r in self.relations],
        }
