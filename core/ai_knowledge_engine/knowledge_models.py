from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class KnowledgeState(Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    REJECTED = "rejected"


class ConfidenceLevel(Enum):
    VERY_LOW = 0.1
    LOW = 0.3
    MEDIUM = 0.5
    HIGH = 0.7
    VERY_HIGH = 0.9
    CERTAIN = 1.0


class KnowledgeType(Enum):
    RESEARCH = "research"
    DOCUMENT = "document"
    EXPERIENCE = "experience"
    INFERENCE = "inference"
    EXPLICIT = "explicit"


@dataclass
class KnowledgeSource:
    id: str
    title: str
    url: str = ""
    source_type: str = ""
    author: str = ""
    published_date: Optional[datetime] = None
    retrieval_date: datetime = field(default_factory=datetime.utcnow)
    reliability_score: float = 0.5
    content_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmbeddingVector:
    id: str
    vector: List[float] = field(default_factory=list)
    dimension: int = 0
    model_name: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeEntry:
    id: str
    title: str
    content: str
    knowledge_type: KnowledgeType = KnowledgeType.EXPLICIT
    state: KnowledgeState = KnowledgeState.PENDING
    confidence: float = 0.0
    source: Optional[KnowledgeSource] = None
    embedding: Optional[EmbeddingVector] = None
    tags: List[str] = field(default_factory=list)
    domain: str = "general"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    related_ids: List[str] = field(default_factory=list)

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


@dataclass
class KnowledgeNode:
    id: str
    entry_id: str
    label: str
    concept: str = ""
    node_type: str = "concept"
    confidence: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class KnowledgeEdge:
    id: str
    source_id: str
    target_id: str
    relation_type: str = "related_to"
    weight: float = 1.0
    confidence: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class KnowledgeGraph:
    id: str
    name: str = ""
    nodes: List[KnowledgeNode] = field(default_factory=list)
    edges: List[KnowledgeEdge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_node(self, node: KnowledgeNode) -> None:
        self.nodes.append(node)
        self.updated_at = datetime.utcnow()

    def add_edge(self, edge: KnowledgeEdge) -> None:
        self.edges.append(edge)
        self.updated_at = datetime.utcnow()


@dataclass
class ResearchQuery:
    id: str
    query: str
    domain: str = "general"
    max_sources: int = 10
    depth: str = "standard"
    filters: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "query": self.query,
            "domain": self.domain,
            "max_sources": self.max_sources,
            "depth": self.depth,
            "filters": self.filters,
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "user_id": self.user_id,
        }


@dataclass
class ResearchResult:
    id: str
    query_id: str
    query: str
    findings: List[Dict[str, Any]] = field(default_factory=list)
    sources: List[KnowledgeSource] = field(default_factory=list)
    summary: str = ""
    confidence: float = 0.0
    processing_time_ms: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchPlan:
    id: str
    query_id: str
    query: str
    steps: List[Dict[str, Any]] = field(default_factory=list)
    hypotheses: List[str] = field(default_factory=list)
    sources_to_check: List[str] = field(default_factory=list)
    methodology: str = "systematic_review"
    estimated_duration_seconds: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DocumentAnalysis:
    id: str
    document_id: str
    title: str = ""
    content: str = ""
    summary: str = ""
    entities: Dict[str, List[str]] = field(default_factory=dict)
    topics: List[str] = field(default_factory=list)
    sentiment: Optional[float] = None
    language: str = "en"
    page_count: int = 0
    word_count: int = 0
    readability_score: float = 0.0
    key_findings: List[str] = field(default_factory=list)
    confidence: float = 0.0
    processing_time_ms: float = 0.0
    analyzed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class VectorMemory:
    id: str
    vectors: List[EmbeddingVector] = field(default_factory=list)
    dimension: int = 768
    index_type: str = "hnsw"
    metric: str = "cosine"
    entry_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Hypothesis:
    id: str
    statement: str
    confidence: float = 0.5
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    status: str = "proposed"
    created_at: datetime = field(default_factory=datetime.utcnow)
    tested_at: Optional[datetime] = None
    reasoning_chain: List[str] = field(default_factory=list)


@dataclass
class ReasoningResult:
    id: str
    query: str
    conclusion: str = ""
    hypotheses: List[Hypothesis] = field(default_factory=list)
    selected_hypothesis: Optional[str] = None
    confidence: float = 0.0
    reasoning_type: str = "deductive"
    reasoning_chain: List[str] = field(default_factory=list)
    processing_time_ms: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningFeedback:
    id: str
    entry_id: str
    feedback_type: str = "relevance"
    score: float = 0.0
    comment: str = ""
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    id: str
    entry_id: str
    valid: bool = False
    confidence: float = 0.0
    checks_passed: List[str] = field(default_factory=list)
    checks_failed: List[str] = field(default_factory=list)
    validator: str = ""
    notes: str = ""
    validated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConfidenceScore:
    value: float = 0.0
    level: ConfidenceLevel = ConfidenceLevel.VERY_LOW
    factors: Dict[str, float] = field(default_factory=dict)
    source_reliability: float = 0.0
    consistency_score: float = 0.0
    recency_score: float = 0.0
    validation_score: float = 0.0

    def calculate_level(self) -> None:
        if self.value >= 0.9:
            self.level = ConfidenceLevel.CERTAIN
        elif self.value >= 0.7:
            self.level = ConfidenceLevel.VERY_HIGH
        elif self.value >= 0.5:
            self.level = ConfidenceLevel.HIGH
        elif self.value >= 0.3:
            self.level = ConfidenceLevel.MEDIUM
        elif self.value >= 0.1:
            self.level = ConfidenceLevel.LOW
        else:
            self.level = ConfidenceLevel.VERY_LOW


@dataclass
class KnowledgeSummary:
    total_entries: int = 0
    active_entries: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)
    by_domain: Dict[str, int] = field(default_factory=dict)
    by_state: Dict[str, int] = field(default_factory=dict)
    avg_confidence: float = 0.0
    total_sources: int = 0
    graph_nodes: int = 0
    graph_edges: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)