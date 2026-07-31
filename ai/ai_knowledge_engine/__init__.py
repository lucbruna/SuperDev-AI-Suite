"""AI Research & Knowledge Engine — Autonomous knowledge and learning platform."""

# Core models
from .knowledge_models import (
    KnowledgeType, SourceType, ConfidenceLevel, ValidationStatus, LearningPhase,
    Knowledge, Document, ResearchQuery, ResearchResult, LearningExperience, EmbeddingVector,
)

# Core engines
from .knowledge_engine import KnowledgeEngine
from .research_engine import ResearchEngine
from .knowledge_manager import KnowledgeManager

# Subsystems
from .research import ResearchSubEngine
from .documents import DocumentSubEngine
from .vector_memory import VectorSubEngine
from .embeddings import EmbeddingSubEngine
from .reasoning import ReasoningSubEngine
from .learning import LearningSubEngine
from .validation import ValidationSubEngine
from .knowledge_graph import GraphSubEngine

# Infrastructure
from .knowledge_config import KnowledgeConfig
from .knowledge_factory import KnowledgeFactory
from .knowledge_registry import KnowledgeRegistry
from .knowledge_runtime import KnowledgeRuntime
from .knowledge_context import KnowledgeContext
from .knowledge_events import KnowledgeEvent, KnowledgeEventType
from .knowledge_metrics import KnowledgeMetrics
from .knowledge_logger import KnowledgeLogger
from .knowledge_security import KnowledgeSecurity

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
