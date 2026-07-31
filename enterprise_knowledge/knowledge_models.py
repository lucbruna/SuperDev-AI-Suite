"""Data models for the Knowledge Graph & Enterprise Memory Engine (Volume 27)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeType(Enum):
    PERSON = "person"
    PROJECT = "project"
    CODE = "code"
    DECISION = "decision"
    DOCUMENT = "document"
    SOLUTION = "solution"
    PROBLEM = "problem"
    SYSTEM = "system"
    COMPANY = "company"
    DATABASE = "database"
    TEAM = "team"
    AGENT = "agent"
    CONCEPT = "concept"
    MEETING = "meeting"
    CONTRACT = "contract"
    POLICY = "policy"


class RelationshipType(Enum):
    CONNECTED_TO = "connected_to"
    USES = "uses"
    HAS = "has"
    OWNS = "owns"
    RESOLVED_BY = "resolved_by"
    FIXED_IN = "fixed_in"
    RELATES_TO = "relates_to"
    IMPLEMENTS = "implements"
    DEPENDS_ON = "depends_on"
    CAUSES = "causes"
    DECIDED_IN = "decided_in"
    DOCUMENTS = "documents"
    BELONGS_TO = "belongs_to"


class MemoryType(Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class SearchMode(Enum):
    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class AccessLevel(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class DocumentStatus(Enum):
    PENDING = "pending"
    INDEXED = "indexed"
    FAILED = "failed"


class IndexStatus(Enum):
    SYNCED = "synced"
    STALE = "stale"
    FAILED = "failed"


@dataclass
class KnowledgeNode:
    """A node in the knowledge graph (person, project, code, decision...)."""
    node_id: str
    node_type: NodeType = NodeType.CONCEPT
    label: str = ""
    properties: dict[str, Any] = field(default_factory=dict)
    access_level: AccessLevel = AccessLevel.INTERNAL
    created_at: float = 0.0


@dataclass
class RelationshipRecord:
    """A directed edge between two knowledge graph nodes."""
    relationship_id: str
    source_id: str
    target_id: str
    rel_type: RelationshipType = RelationshipType.CONNECTED_TO
    properties: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0


@dataclass
class MemoryRecord:
    """A memory item (short/long-term, episodic or semantic)."""
    memory_id: str
    memory_type: MemoryType = MemoryType.SEMANTIC
    content: str = ""
    owner_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5  # 0..1
    access_count: int = 0
    created_at: float = 0.0
    last_accessed_at: float = 0.0


@dataclass
class DocumentRecord:
    """A knowledge document (pdf, docx, csv, code, image, contract...)."""
    document_id: str
    title: str = ""
    content: str = ""
    source: str = ""
    file_type: str = "txt"
    tags: list[str] = field(default_factory=list)
    status: DocumentStatus = DocumentStatus.PENDING
    access_level: AccessLevel = AccessLevel.INTERNAL
    created_at: float = 0.0


@dataclass
class SearchResult:
    """Ranked search hits."""
    query: str = ""
    hits: list[dict[str, Any]] = field(default_factory=list)
    total: int = 0
    mode: SearchMode = SearchMode.HYBRID


@dataclass
class ExtractionResult:
    """Entities and relations extracted from a document/text."""
    entities: list[dict[str, Any]] = field(default_factory=list)
    relations: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""


@dataclass
class ReasoningResult:
    """A conclusion with evidence and explanation."""
    conclusion: str = ""
    confidence: float = 0.0  # 0..1
    evidence: list[str] = field(default_factory=list)
    explanation: str = ""
    hypotheses: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class IndexEntry:
    """An entry in the knowledge index."""
    index_id: str
    target_id: str
    terms: dict[str, int] = field(default_factory=dict)
    status: IndexStatus = IndexStatus.SYNCED
    updated_at: float = 0.0


@dataclass
class AuditRecord:
    """Governance audit entry."""
    audit_id: str
    actor: str = ""
    action: str = ""
    target: str = ""
    access_level: AccessLevel = AccessLevel.INTERNAL
    outcome: str = "allowed"
    created_at: float = 0.0


@dataclass
class GovernancePolicy:
    """A governance rule (access, classification, retention)."""
    policy_id: str
    name: str = ""
    policy_type: str = "access"  # access|classification|retention
    access_level: AccessLevel = AccessLevel.INTERNAL
    retention_days: int = 0
    rules: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
