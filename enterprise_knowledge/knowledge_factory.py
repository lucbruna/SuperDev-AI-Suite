"""Factory for the Knowledge Graph & Enterprise Memory Engine."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_config import EnterpriseKnowledgeConfig
from enterprise_knowledge.knowledge_context import EnterpriseKnowledgeContext
from enterprise_knowledge.knowledge_engine import EnterpriseKnowledgeEngine
from enterprise_knowledge.knowledge_events import EnterpriseKnowledgeEvents
from enterprise_knowledge.knowledge_metrics import EnterpriseKnowledgeMetrics
from enterprise_knowledge.knowledge_registry import EnterpriseKnowledgeRegistry
from enterprise_knowledge.knowledge_runtime import EnterpriseKnowledgeRuntime
from enterprise_knowledge.knowledge_security import EnterpriseKnowledgeSecurity


def build_engine(config: dict[str, Any] | None = None) -> EnterpriseKnowledgeEngine:
    """Builds a fully wired EnterpriseKnowledgeEngine."""
    return EnterpriseKnowledgeEngine(
        config=EnterpriseKnowledgeConfig(**(config or {})),
        events=EnterpriseKnowledgeEvents(),
        metrics=EnterpriseKnowledgeMetrics(),
        registry=EnterpriseKnowledgeRegistry(),
        security=EnterpriseKnowledgeSecurity(),
        context=EnterpriseKnowledgeContext(),
        runtime=EnterpriseKnowledgeRuntime())
