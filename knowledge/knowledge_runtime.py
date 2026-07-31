from __future__ import annotations

import logging
from typing import Any

from .knowledge_config import KnowledgeConfig
from .knowledge_events import KnowledgeEvents
from .knowledge_factory import KnowledgeFactory
from .knowledge_manager import KnowledgeManager
from .knowledge_metrics import KnowledgeMetrics
from .knowledge_registry import KnowledgeRegistry
from .knowledge_security import KnowledgeSecurity


class KnowledgeRuntime:
    """Runtime lifecycle and composition root for the knowledge engine."""

    def __init__(self, config: KnowledgeConfig | None = None) -> None:
        self._log = logging.getLogger("superdev.knowledge.runtime")
        self.config = config or KnowledgeConfig()
        self.events = KnowledgeEvents()
        self.metrics = KnowledgeMetrics()
        self.registry = KnowledgeRegistry()
        self.security = KnowledgeSecurity(self.config.enable_governance)
        self.manager: KnowledgeManager | None = None
        self.factory: KnowledgeFactory | None = None
        self._started = False

    def start(self) -> "KnowledgeRuntime":
        if self._started:
            return self
        self.factory = KnowledgeFactory(self.config, self.registry)
        self.manager = self.factory.build_manager()
        self._started = True
        self._log.info("knowledge runtime started (workspace=%s)", self.config.workspace_id)
        return self

    def stop(self) -> None:
        self._started = False
        self._log.info("knowledge runtime stopped")

    def status(self) -> dict[str, Any]:
        manager = self.manager
        base = {
            "started": self._started,
            "workspace_id": self.config.workspace_id,
        }
        if manager is not None:
            base.update(manager.status())
        return base

    @property
    def is_running(self) -> bool:
        return self._started and self.manager is not None
