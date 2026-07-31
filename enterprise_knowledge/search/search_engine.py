"""Search engine: keyword + semantic + hybrid queries with ranking."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_config import EnterpriseKnowledgeConfig
from enterprise_knowledge.knowledge_events import (EnterpriseKnowledgeEvents,
                                                   EnterpriseKnowledgeEventType)
from enterprise_knowledge.knowledge_logger import get_logger
from enterprise_knowledge.knowledge_metrics import EnterpriseKnowledgeMetrics
from enterprise_knowledge.knowledge_models import AccessLevel, SearchMode
from enterprise_knowledge.knowledge_security import EnterpriseKnowledgeSecurity
from enterprise_knowledge.search.filters import SearchFilters
from enterprise_knowledge.search.keyword_search import KeywordSearch
from enterprise_knowledge.search.ranking import SearchRanking
from enterprise_knowledge.search.semantic_search import SemanticSearch
from enterprise_knowledge.search.suggestions import SearchSuggestions
from enterprise_knowledge.vector.vector_engine import VectorEngine


class SearchEngine:
    """Orquestrador de busca (Fase 5 do Volume 27)."""

    def __init__(self, events: EnterpriseKnowledgeEvents | None = None,
                 metrics: EnterpriseKnowledgeMetrics | None = None,
                 config: EnterpriseKnowledgeConfig | None = None,
                 security: EnterpriseKnowledgeSecurity | None = None,
                 vectors: VectorEngine | None = None) -> None:
        self._log = get_logger("search")
        self.events = events or EnterpriseKnowledgeEvents()
        self.metrics = metrics or EnterpriseKnowledgeMetrics()
        self.config = config or EnterpriseKnowledgeConfig()
        self.security = security or EnterpriseKnowledgeSecurity()
        self.vectors = vectors
        self.keyword = KeywordSearch()
        self.semantic = SemanticSearch(vectors=vectors)
        self.ranking = SearchRanking()
        self.filters = SearchFilters()
        self.suggestions = SearchSuggestions()

    def search(self, query: str, mode: SearchMode = SearchMode.HYBRID,
               limit: int = 10,
               filters: dict[str, Any] | None = None,
               min_access: AccessLevel = AccessLevel.PUBLIC) -> list[dict[str, Any]]:
        keyword_hits = []
        if mode in (SearchMode.KEYWORD, SearchMode.HYBRID):
            records = self._records_for_keyword()
            keyword_hits = self.keyword.search(query, records, limit=limit)
        semantic_hits = []
        if mode in (SearchMode.SEMANTIC, SearchMode.HYBRID):
            semantic_hits = self.semantic.search(query, limit=limit)
        if mode == SearchMode.HYBRID:
            results = self.ranking.fuse(keyword_hits, semantic_hits,
                                        limit=limit)
        elif mode == SearchMode.KEYWORD:
            results = keyword_hits
        else:
            results = semantic_hits
        results = self.filters.apply(results, filters=filters,
                                     min_access=min_access)
        # Vector queries already count ek.searches; count here only when the
        # vector engine did not run (no vectors or pure keyword mode).
        if self.vectors is None or mode == SearchMode.KEYWORD:
            self.metrics.increment("ek.searches")
        self.events.publish(EnterpriseKnowledgeEventType.SEARCH_EXECUTED,
                            {"query": query, "mode": mode.value,
                             "hits": len(results)})
        return results

    def _records_for_keyword(self) -> list[dict[str, Any]]:
        if self.vectors is None:
            return []
        return [{"id": item["vector_id"], "text": item.get("metadata", {}).get(
            "text", ""), "metadata": item.get("metadata", {})}
            for item in self.vectors.database.all()]

    def suggest(self, prefix: str, limit: int = 5) -> list[str]:
        return self.suggestions.suggest(prefix, limit=limit)

    def learn(self, texts: list[str]) -> None:
        self.suggestions.learn(texts)

    def stats(self) -> dict[str, Any]:
        return {"searches": self.metrics.snapshot()["counters"].get(
            "ek.searches", 0),
            "vocabulary": len(self.suggestions.vocabulary)}
