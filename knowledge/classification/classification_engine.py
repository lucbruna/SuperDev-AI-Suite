from __future__ import annotations

import logging
from typing import Any

from ..knowledge_config import KnowledgeConfig
from ..knowledge_events import KnowledgeEvents, KnowledgeEventType
from ..knowledge_metrics import KnowledgeMetrics
from .category_manager import Category, CategoryManager
from .classifier import Classifier
from .scorer import Scorer


class ClassificationEngine:
    """Composes category management, scoring, and classification."""

    def __init__(
        self,
        config: KnowledgeConfig | None = None,
        events: KnowledgeEvents | None = None,
        metrics: KnowledgeMetrics | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.classification.engine")
        self.config = config or KnowledgeConfig()
        self.events = events or KnowledgeEvents()
        self.metrics = metrics or KnowledgeMetrics()
        self.category_manager = CategoryManager()
        self.classifier = Classifier(self.category_manager, Scorer())

    def add_category(self, name: str, keywords: list[str], weight: float = 1.0) -> None:
        self.category_manager.add(Category(name=name, keywords=keywords, weight=weight))

    def classify(self, text: str, threshold: float = 0.0, top_k: int = 0) -> list[dict[str, Any]]:
        results = self.classifier.classify(text, threshold=threshold, top_k=top_k)
        self.metrics.increment("classification.executed")
        self.events.emit(KnowledgeEventType.EMBEDDING_CREATED, {"classified": len(results)})
        return results

    def stats(self) -> dict[str, Any]:
        return {"categories": self.category_manager.names()}
