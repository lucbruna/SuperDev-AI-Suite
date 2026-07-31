"""Knowledge Engine Models — Core data models for the knowledge platform."""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class KnowledgeType(Enum):
    FACT = "fact"
    CONCEPT = "concept"
    PROCEDURE = "procedure"
    RULE = "rule"
    PATTERN = "pattern"
    EXPERIENCE = "experience"
    INSIGHT = "insight"
    HYPOTHESIS = "hypothesis"


class SourceType(Enum):
    WEB = "web"
    DOCUMENT = "document"
    DATABASE = "database"
    API = "api"
    USER_INPUT = "user_input"
    AGENT_EXPERIENCE = "agent_experience"
    EXTERNAL_SERVICE = "external_service"


class ConfidenceLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERIFIED = "verified"


class ValidationStatus(Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"
    OUTDATED = "outdated"


class LearningPhase(Enum):
    COLLECTION = "collection"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    VALIDATION = "validation"
    INTEGRATION = "integration"
    DEPLOYMENT = "deployment"


@dataclass
class Knowledge:
    knowledge_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    content: str = ""
    knowledge_type: KnowledgeType = KnowledgeType.FACT
    source: SourceType = SourceType.USER_INPUT
    source_reference: str = ""
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    validation_status: ValidationStatus = ValidationStatus.PENDING
    tags: List[str] = field(default_factory=list)
    embeddings: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    related_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    accessed_at: Optional[datetime] = None
    access_count: int = 0
    version: int = 1


@dataclass
class Document:
    document_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    content: str = ""
    document_type: str = "text"
    source_path: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunks: List[str] = field(default_factory=list)
    summary: str = ""
    keywords: List[str] = field(default_factory=list)
    processed: bool = False
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResearchQuery:
    query_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    query_text: str = ""
    query_type: str = "info"
    parameters: Dict[str, Any] = field(default_factory=dict)
    max_results: int = 10
    sources: List[SourceType] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResearchResult:
    result_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    query_id: str = ""
    title: str = ""
    content: str = ""
    source: SourceType = SourceType.WEB
    source_url: str = ""
    relevance_score: float = 0.0
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    metadata: Dict[str, Any] = field(default_factory=dict)
    collected_at: datetime = field(default_factory=datetime.now)


@dataclass
class LearningExperience:
    experience_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    outcome: str = ""
    success: bool = True
    lessons: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    phase: LearningPhase = LearningPhase.COLLECTION
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EmbeddingVector:
    vector_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    text: str = ""
    vector: List[float] = field(default_factory=list)
    model: str = "default"
    dimensions: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
