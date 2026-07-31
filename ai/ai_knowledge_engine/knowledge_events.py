"""Knowledge Engine Events — Event definitions for knowledge operations."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class KnowledgeEventType(Enum):
    KNOWLEDGE_STORED = "knowledge_stored"
    KNOWLEDGE_UPDATED = "knowledge_updated"
    KNOWLEDGE_DELETED = "knowledge_deleted"
    KNOWLEDGE_SEARCHED = "knowledge_searched"
    DOCUMENT_PROCESSED = "document_processed"
    RESEARCH_STARTED = "research_started"
    RESEARCH_COMPLETED = "research_completed"
    VALIDATION_PASSED = "validation_passed"
    VALIDATION_FAILED = "validation_failed"
    LEARNING_RECORDED = "learning_recorded"
    EMBEDDING_CREATED = "embedding_created"
    GRAPH_UPDATED = "graph_updated"


@dataclass
class KnowledgeEvent:
    event_id: str = ""
    event_type: KnowledgeEventType = KnowledgeEventType.KNOWLEDGE_STORED
    source: str = ""
    target: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
