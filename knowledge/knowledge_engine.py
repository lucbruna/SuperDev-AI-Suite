from __future__ import annotations

import logging
from typing import Any

from .knowledge_config import KnowledgeConfig
from .knowledge_context import KnowledgeContext, KnowledgeResult
from .knowledge_events import KnowledgeEvents
from .knowledge_manager import KnowledgeManager
from .knowledge_metrics import KnowledgeMetrics
from .knowledge_registry import KnowledgeRegistry
from .knowledge_runtime import KnowledgeRuntime
from .knowledge_security import KnowledgeSecurity


class KnowledgeEngine:
    """Top-level facade for the Knowledge & Memory Engine."""

    def __init__(
        self,
        config: KnowledgeConfig | None = None,
        runtime: KnowledgeRuntime | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.engine")
        self.config = config or KnowledgeConfig()
        self.runtime = runtime or KnowledgeRuntime(self.config)
        self.events: KnowledgeEvents = self.runtime.events
        self.metrics: KnowledgeMetrics = self.runtime.metrics
        self.registry: KnowledgeRegistry = self.runtime.registry
        self.security: KnowledgeSecurity = self.runtime.security

    def initialize(self) -> "KnowledgeEngine":
        self.runtime.start()
        return self

    @property
    def manager(self) -> KnowledgeManager | None:
        return self.runtime.manager

    def store(self, content: str, memory_type: str = "episodic", importance: float = 0.5,
              metadata: dict[str, Any] | None = None) -> KnowledgeResult:
        try:
            if self.manager is None:
                return KnowledgeResult.fail("store", "engine not initialized")
            record_id = self.manager.store_memory(content, memory_type, importance, metadata)
            return KnowledgeResult.ok("store", {"record_id": record_id})
        except Exception as exc:  # noqa: BLE001
            return KnowledgeResult.fail("store", str(exc))

    def recall(self, memory_type: str | None = None) -> KnowledgeResult:
        try:
            if self.manager is None:
                return KnowledgeResult.fail("recall", "engine not initialized")
            records = self.manager.recall_memory(memory_type)
            return KnowledgeResult.ok("recall", records)
        except Exception as exc:  # noqa: BLE001
            return KnowledgeResult.fail("recall", str(exc))

    def search(self, query: str, top_k: int = 5, context: KnowledgeContext | None = None) -> KnowledgeResult:
        try:
            if self.manager is None:
                return KnowledgeResult.fail("search", "engine not initialized")
            results = self.manager.search(query, top_k=top_k)
            return KnowledgeResult.ok("search", results)
        except Exception as exc:  # noqa: BLE001
            return KnowledgeResult.fail("search", str(exc))

    def status(self) -> dict[str, Any]:
        return self.runtime.status()

    def shutdown(self) -> None:
        self.runtime.stop()
