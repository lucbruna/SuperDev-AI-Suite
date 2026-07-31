from __future__ import annotations

import logging
from typing import Any

from ..knowledge_config import KnowledgeConfig
from ..knowledge_events import KnowledgeEvents, KnowledgeEventType
from ..knowledge_metrics import KnowledgeMetrics
from .index_manager import IndexManager
from .index_updater import IndexUpdater
from .indexer import Indexer


class IndexingEngine:
    """Composes the index family and exposes search over indexed content."""

    def __init__(
        self,
        config: KnowledgeConfig | None = None,
        events: KnowledgeEvents | None = None,
        metrics: KnowledgeMetrics | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.indexing.engine")
        self.config = config or KnowledgeConfig()
        self.events = events or KnowledgeEvents()
        self.metrics = metrics or KnowledgeMetrics()
        self.index_manager = IndexManager()
        self.indexer = Indexer(self.index_manager)
        self.updater = IndexUpdater(self.index_manager)

    def add_document(self, document: Any) -> str:
        document_id = self.indexer.index_document(document)
        self.metrics.increment("indexing.added")
        self.events.emit(KnowledgeEventType.INDEX_UPDATED, {"document_id": document_id})
        return document_id

    def add_chunks(self, chunks: list[Any]) -> list[str]:
        document_ids = self.indexer.index_chunks(chunks)
        self.metrics.increment("indexing.chunks", len(document_ids))
        self.events.emit(KnowledgeEventType.INDEX_UPDATED, {"chunks": len(document_ids)})
        return document_ids

    def remove(self, document_id: str) -> None:
        self.index_manager.remove(document_id)
        self.metrics.increment("indexing.removed")

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        hits = self.updater.keyword_search(query, top_k=top_k)
        self.metrics.increment("indexing.searches")
        return hits

    def stats(self) -> dict[str, Any]:
        return self.index_manager.stats()

    def clear(self) -> None:
        self.index_manager.clear()
