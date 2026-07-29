"""
SuperDev AI Knowledge Engine

Enterprise knowledge intelligence platform providing:
- Knowledge acquisition & research automation
- Document analysis & entity extraction
- Vector embeddings & semantic search
- Knowledge graph construction & traversal
- Multi-strategy reasoning & hypothesis testing
- Continuous learning from feedback
- Knowledge validation & confidence scoring
"""

from .knowledge_engine import KnowledgeEngine, KnowledgeEngineConfig, KnowledgeEngineState, KnowledgeEngineMetrics
from .knowledge_manager import KnowledgeManager, ManagerConfig
from .knowledge_config import (
    KnowledgeConfig, ResearchConfig, DocumentConfig, VectorMemoryConfig,
    EmbeddingConfig, ReasoningConfig, LearningConfig, ValidationConfig, KnowledgeGraphConfig,
)
from .knowledge_models import (
    KnowledgeType, KnowledgeState, ConfidenceLevel,
    KnowledgeEntry, KnowledgeSource, KnowledgeGraph, KnowledgeNode, KnowledgeEdge,
    ResearchQuery, ResearchResult, ResearchPlan, DocumentAnalysis,
    VectorMemory, EmbeddingVector, ReasoningResult, Hypothesis,
    LearningFeedback, ValidationResult, ConfidenceScore, KnowledgeSummary,
)
from .knowledge_security import (
    KnowledgeSecurityManager, AccessController, SourceValidator,
    KnowledgeClassifier, AuditTrail, ApprovalManager,
    KnowledgeClassification, AccessAction, AuditEntry, ApprovalRequest,
)
from .knowledge_events import KnowledgeEventBus, KnowledgeEvent, EventType
from .knowledge_metrics import KnowledgeMetrics, MetricsCollector
from .knowledge_context import KnowledgeContext
from .knowledge_interfaces import (
    IKnowledgeSource, IKnowledgeProcessor, IKnowledgeStorage, IKnowledgeValidator,
    ConcreteKnowledgeSource, ConcreteKnowledgeProcessor,
    ConcreteKnowledgeStorage, ConcreteKnowledgeValidator,
)
from .knowledge_protocols import KnowledgeProtocol, ResearchProtocol, LearningProtocol, ValidationProtocol, IntegrationProtocol
from .knowledge_logger import KnowledgeLogger, LogEntry, LogLevel
from .knowledge_registry import KnowledgeRegistry
from .knowledge_factory import KnowledgeFactory
from .knowledge_runtime import KnowledgeRuntime, RuntimeState, RuntimeStats
from .research_engine import ResearchEngine, EngineConfig as ResearchEngineConfig, EngineMetrics as ResearchEngineMetrics, EngineState as ResearchEngineState

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

__all__ = [
    "KnowledgeEngine", "KnowledgeEngineConfig", "KnowledgeEngineState", "KnowledgeEngineMetrics",
    "KnowledgeManager", "ManagerConfig",
    "KnowledgeConfig", "ResearchConfig", "DocumentConfig", "VectorMemoryConfig",
    "EmbeddingConfig", "ReasoningConfig", "LearningConfig", "ValidationConfig", "KnowledgeGraphConfig",
    "KnowledgeType", "KnowledgeState", "ConfidenceLevel",
    "KnowledgeEntry", "KnowledgeSource", "KnowledgeGraph", "KnowledgeNode", "KnowledgeEdge",
    "ResearchQuery", "ResearchResult", "ResearchPlan", "DocumentAnalysis",
    "VectorMemory", "EmbeddingVector", "ReasoningResult", "Hypothesis",
    "LearningFeedback", "ValidationResult", "ConfidenceScore", "KnowledgeSummary",
    "KnowledgeSecurityManager", "AccessController", "SourceValidator",
    "KnowledgeClassifier", "AuditTrail", "ApprovalManager",
    "KnowledgeClassification", "AccessAction", "AuditEntry", "ApprovalRequest",
    "KnowledgeEventBus", "KnowledgeEvent", "EventType",
    "KnowledgeMetrics", "MetricsCollector",
    "KnowledgeContext",
    "IKnowledgeSource", "IKnowledgeProcessor", "IKnowledgeStorage", "IKnowledgeValidator",
    "ConcreteKnowledgeSource", "ConcreteKnowledgeProcessor",
    "ConcreteKnowledgeStorage", "ConcreteKnowledgeValidator",
    "KnowledgeProtocol", "ResearchProtocol", "LearningProtocol", "ValidationProtocol", "IntegrationProtocol",
    "KnowledgeLogger", "LogEntry", "LogLevel",
    "KnowledgeRegistry",
    "KnowledgeFactory",
    "KnowledgeRuntime", "RuntimeState", "RuntimeStats",
    "ResearchEngine", "ResearchEngineConfig", "ResearchEngineMetrics", "ResearchEngineState",
]