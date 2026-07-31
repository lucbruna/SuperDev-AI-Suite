"""Indexing engine: crawls sources and keeps the index synchronized."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.indexing.crawler import KnowledgeCrawler
from enterprise_knowledge.indexing.scheduler import IndexScheduler
from enterprise_knowledge.indexing.synchronization import IndexSynchronization
from enterprise_knowledge.indexing.updater import IndexUpdater
from enterprise_knowledge.knowledge_config import EnterpriseKnowledgeConfig
from enterprise_knowledge.knowledge_events import (EnterpriseKnowledgeEvents,
                                                   EnterpriseKnowledgeEventType)
from enterprise_knowledge.knowledge_logger import get_logger
from enterprise_knowledge.knowledge_metrics import EnterpriseKnowledgeMetrics
from enterprise_knowledge.knowledge_registry import EnterpriseKnowledgeRegistry
from enterprise_knowledge.knowledge_security import EnterpriseKnowledgeSecurity


class IndexingEngine:
    """Orquestrador de indexação (Fase 9 do Volume 27)."""

    def __init__(self, events: EnterpriseKnowledgeEvents | None = None,
                 metrics: EnterpriseKnowledgeMetrics | None = None,
                 config: EnterpriseKnowledgeConfig | None = None,
                 security: EnterpriseKnowledgeSecurity | None = None,
                 registry: EnterpriseKnowledgeRegistry | None = None) -> None:
        self._log = get_logger("indexing")
        self.events = events or EnterpriseKnowledgeEvents()
        self.metrics = metrics or EnterpriseKnowledgeMetrics()
        self.config = config or EnterpriseKnowledgeConfig()
        self.security = security or EnterpriseKnowledgeSecurity()
        self.registry = registry
        self.crawler = KnowledgeCrawler()
        self.updater = IndexUpdater(registry=registry)
        self.scheduler = IndexScheduler(
            frequency_seconds=self.config.get("index_frequency_seconds", 300))
        self.synchronizer = IndexSynchronization()

    def add_source(self, source_id: str,
                   documents: list[dict[str, Any]] | None = None) -> None:
        self.crawler.add_source(source_id, documents)

    def refresh(self) -> dict[str, Any]:
        crawled = self.crawler.crawl()
        indexed_ids = self._indexed_targets()
        diff = self.synchronizer.diff(indexed_ids, crawled)
        for document in crawled:
            if document["document_id"] in diff["to_index"]:
                self.updater.upsert(document["document_id"],
                                    document["content"])
        if diff["to_remove"]:
            for target in diff["to_remove"]:
                self._remove_for_target(target)
        if self.synchronizer.needs_refresh(diff):
            self.metrics.increment("ek.index_entries",
                                   len(diff["to_index"]))
            self.events.publish(EnterpriseKnowledgeEventType.INDEX_UPDATED,
                                {"indexed": len(diff["to_index"]),
                                 "removed": len(diff["to_remove"])})
        return {"indexed": len(diff["to_index"]),
                "removed": len(diff["to_remove"]),
                "synced": len(diff["synced"])}

    def _indexed_targets(self) -> list[str]:
        if self.registry is None:
            return []
        targets = []
        for index_id in self.registry.list_index():
            entry = self.registry.get_index(index_id)
            if entry is not None:
                targets.append(entry.target_id)
        return targets

    def _remove_for_target(self, target_id: str) -> None:
        if self.registry is None:
            return
        for index_id in self.registry.list_index():
            entry = self.registry.get_index(index_id)
            if entry is not None and entry.target_id == target_id:
                self.registry.remove_index(index_id)

    def mark_stale(self, target_id: str) -> bool:
        return self.updater.mark_stale(target_id)

    def search_index(self, term: str, limit: int = 5) -> list[dict[str, Any]]:
        if self.registry is None:
            return []
        hits = []
        for index_id in self.registry.list_index():
            entry = self.registry.get_index(index_id)
            if entry is None or term not in entry.terms:
                continue
            hits.append({"index_id": index_id, "target_id": entry.target_id,
                         "term": term, "count": entry.terms[term]})
        hits.sort(key=lambda hit: hit["count"], reverse=True)
        return hits[:max(0, limit)]

    def stats(self) -> dict[str, Any]:
        return {"sources": self.crawler.source_count(),
                "entries": len(self._indexed_targets()),
                "scheduler_runs": self.scheduler.runs,
                "counters": self.metrics.snapshot()["counters"]}
