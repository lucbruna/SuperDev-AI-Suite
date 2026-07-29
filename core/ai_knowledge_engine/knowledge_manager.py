from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .knowledge_config import KnowledgeConfig
from .knowledge_context import KnowledgeContext
from .knowledge_engine import KnowledgeEngine, KnowledgeEngineConfig, KnowledgeEngineState, KnowledgeEngineMetrics
from .knowledge_events import KnowledgeEventBus, KnowledgeEvent, EventType
from .knowledge_metrics import KnowledgeMetrics, MetricsCollector
from .knowledge_models import (
    KnowledgeEntry, KnowledgeType, KnowledgeState, ResearchQuery,
    ResearchResult, DocumentAnalysis, ValidationResult, KnowledgeSummary,
)
from .knowledge_security import KnowledgeSecurityManager
from .knowledge_logger import KnowledgeLogger, LogLevel

logger = logging.getLogger(__name__)


@dataclass
class ManagerConfig:
    engine_config: KnowledgeEngineConfig
    enable_auto_research: bool = True
    enable_auto_learning: bool = True
    enable_knowledge_sync: bool = True
    max_concurrent_operations: int = 10


class KnowledgeManager:
    def __init__(self, config: ManagerConfig):
        self.config = config
        self.engine = KnowledgeEngine(config.engine_config)
        self.security = config.engine_config.security
        self.context = self.engine.context
        self.event_bus = config.engine_config.event_bus
        self.logger = config.engine_config.logger
        self.metrics = config.engine_config.metrics_collector
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return
        await self.engine.initialize()
        await self.engine.start()
        self._initialized = True
        self.logger.info("manager", "Knowledge Manager initialized")

    async def shutdown(self) -> None:
        await self.engine.stop()
        self._initialized = False
        self.logger.info("manager", "Knowledge Manager shutdown")

    async def search_knowledge(self, query: str, domain: str = "general",
                                limit: int = 10) -> List[KnowledgeEntry]:
        if not self._initialized:
            raise RuntimeError("Knowledge Manager not initialized")
        if not self.security.verify_access("system", "knowledge", "read"):
            raise PermissionError("Access denied")
        return await self.engine.search(query, domain, limit)

    async def store_knowledge(self, title: str, content: str,
                               knowledge_type: KnowledgeType = KnowledgeType.EXPLICIT,
                               domain: str = "general",
                               tags: Optional[List[str]] = None,
                               metadata: Optional[Dict[str, Any]] = None) -> KnowledgeEntry:
        if not self._initialized:
            raise RuntimeError("Knowledge Manager not initialized")
        entry = KnowledgeEntry(
            id=str(uuid.uuid4()),
            title=title,
            content=content,
            knowledge_type=knowledge_type,
            domain=domain,
            tags=tags or [],
            metadata=metadata or {},
        )
        return await self.engine.store(entry)

    async def get_knowledge(self, entry_id: str) -> Optional[KnowledgeEntry]:
        if not self._initialized:
            raise RuntimeError("Knowledge Manager not initialized")
        return await self.engine.retrieve(entry_id)

    async def analyze_document(self, document_id: str, content: str,
                                 title: str = "") -> DocumentAnalysis:
        if not self._initialized:
            raise RuntimeError("Knowledge Manager not initialized")
        return await self.engine.analyze(document_id, content, title)

    async def conduct_research(self, query: str, domain: str = "general",
                                 max_sources: int = 10) -> ResearchResult:
        if not self._initialized:
            raise RuntimeError("Knowledge Manager not initialized")
        research_query = ResearchQuery(
            id=str(uuid.uuid4()),
            query=query,
            domain=domain,
            max_sources=max_sources,
        )
        return await self.engine.research(research_query)

    async def get_recommendations(self, context: str, limit: int = 5) -> List[KnowledgeEntry]:
        if not self._initialized:
            raise RuntimeError("Knowledge Manager not initialized")
        return await self.engine.search(context, "general", limit)

    async def get_knowledge_stats(self) -> KnowledgeMetrics:
        return self.metrics.metrics

    async def get_engine_status(self) -> Dict[str, Any]:
        return self.engine.get_status()

    def is_healthy(self) -> bool:
        return self.engine.metrics.state == KnowledgeEngineState.RUNNING

    async def get_knowledge_summary(self) -> KnowledgeSummary:
        return await self.engine.get_summary()