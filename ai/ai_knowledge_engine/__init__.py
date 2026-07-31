"""AI Research & Knowledge Engine — Autonomous knowledge and learning platform."""

# Core models
from .documents import DocumentSubEngine
from .embeddings import EmbeddingSubEngine

# Infrastructure
from .knowledge_config import KnowledgeConfig
from .knowledge_context import KnowledgeContext

# Core engines
from .knowledge_engine import KnowledgeEngine
from .knowledge_events import KnowledgeEvent, KnowledgeEventType
from .knowledge_factory import KnowledgeFactory
from .knowledge_graph import GraphSubEngine
from .knowledge_logger import KnowledgeLogger
from .knowledge_manager import KnowledgeManager
from .knowledge_metrics import KnowledgeMetrics
from .knowledge_models import (
    ConfidenceLevel,
    Document,
    EmbeddingVector,
    Knowledge,
    KnowledgeType,
    LearningExperience,
    LearningPhase,
    ResearchQuery,
    ResearchResult,
    SourceType,
    ValidationStatus,
)
from .knowledge_registry import KnowledgeRegistry
from .knowledge_runtime import KnowledgeRuntime
from .knowledge_security import KnowledgeSecurity
from .learning import LearningSubEngine
from .reasoning import ReasoningSubEngine

# Subsystems
from .research import ResearchSubEngine
from .research_engine import ResearchEngine
from .validation import ValidationSubEngine
from .vector_memory import VectorSubEngine

__all__ = [
    # Enums
    "KnowledgeType", "SourceType", "ConfidenceLevel", "ValidationStatus", "LearningPhase",
    # Models
    "Knowledge", "Document", "ResearchQuery", "ResearchResult", "LearningExperience", "EmbeddingVector",
    # Core engines
    "KnowledgeEngine", "ResearchEngine", "KnowledgeManager",
    # Subsystems
    "ResearchSubEngine", "DocumentSubEngine", "VectorSubEngine", "EmbeddingSubEngine",
    "ReasoningSubEngine", "LearningSubEngine", "ValidationSubEngine", "GraphSubEngine",
    # Infrastructure
    "KnowledgeConfig", "KnowledgeFactory", "KnowledgeRegistry", "KnowledgeRuntime",
    "KnowledgeContext", "KnowledgeEvent", "KnowledgeEventType",
    "KnowledgeMetrics", "KnowledgeLogger", "KnowledgeSecurity",
]
