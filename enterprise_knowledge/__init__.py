"""Knowledge Graph & Enterprise Memory Engine (Volume 27).

Public API for the enterprise knowledge layer: a connected network where
people, projects, code, decisions, documents and solutions are linked,
with vector memory, document intelligence, semantic search, extraction,
reasoning, indexing and governance.
"""
from __future__ import annotations

from .knowledge_config import EnterpriseKnowledgeConfig
from .knowledge_context import EnterpriseKnowledgeContext
from .knowledge_engine import EnterpriseKnowledgeEngine
from .knowledge_events import (EnterpriseKnowledgeEvents,
                               EnterpriseKnowledgeEventType)
from .knowledge_factory import build_engine
from .knowledge_interfaces import (DocumentParser, EmbeddingProvider,
                                   Extractor, GraphStore, Indexer,
                                   KnowledgeSink, MemoryStore, Reasoner,
                                   SearchProvider, VectorStore)
from .knowledge_logger import get_logger
from .knowledge_manager import EnterpriseKnowledgeManager
from .knowledge_metrics import EnterpriseKnowledgeMetrics
from .knowledge_models import (AccessLevel, AuditRecord, DocumentRecord,
                               DocumentStatus, ExtractionResult,
                               GovernancePolicy, IndexEntry, IndexStatus,
                               KnowledgeNode, MemoryRecord, MemoryType,
                               NodeType, ReasoningResult,
                               RelationshipRecord, RelationshipType,
                               SearchMode, SearchResult)
from .knowledge_protocols import (coerce_bool, coerce_number, new_id,
                                  normalize, safe_get, tokenize, top_n)
from .knowledge_registry import EnterpriseKnowledgeRegistry
from .knowledge_runtime import EnterpriseKnowledgeRuntime
from .knowledge_security import EnterpriseKnowledgeSecurity

__all__ = [
    "AccessLevel",
    "AuditRecord",
    "DocumentParser",
    "DocumentRecord",
    "DocumentStatus",
    "EmbeddingProvider",
    "EnterpriseKnowledgeConfig",
    "EnterpriseKnowledgeContext",
    "EnterpriseKnowledgeEngine",
    "EnterpriseKnowledgeEventType",
    "EnterpriseKnowledgeEvents",
    "EnterpriseKnowledgeManager",
    "EnterpriseKnowledgeMetrics",
    "EnterpriseKnowledgeRegistry",
    "EnterpriseKnowledgeRuntime",
    "EnterpriseKnowledgeSecurity",
    "ExtractionResult",
    "Extractor",
    "GovernancePolicy",
    "GraphStore",
    "IndexEntry",
    "IndexStatus",
    "Indexer",
    "KnowledgeNode",
    "KnowledgeSink",
    "MemoryRecord",
    "MemoryStore",
    "MemoryType",
    "NodeType",
    "Reasoner",
    "ReasoningResult",
    "RelationshipRecord",
    "RelationshipType",
    "SearchMode",
    "SearchProvider",
    "SearchResult",
    "VectorStore",
    "build_engine",
    "coerce_bool",
    "coerce_number",
    "get_logger",
    "new_id",
    "normalize",
    "safe_get",
    "tokenize",
    "top_n",
]
