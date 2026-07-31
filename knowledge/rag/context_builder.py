from __future__ import annotations

import logging

from ..knowledge_models import RetrievalContext, SearchResult


class ContextBuilder:
    """Assembles retrieval context from search results and memory hits."""

    def __init__(self, max_context_chars: int = 4000) -> None:
        self._log = logging.getLogger("superdev.knowledge.rag.context_builder")
        self._max_context_chars = max_context_chars

    def build(self, query: str, results: list[SearchResult], memory_hits: list[str] | None = None) -> RetrievalContext:
        context = RetrievalContext(
            query=query,
            results=list(results),
            memory_hits=list(memory_hits or []),
        )
        return context

    def truncate(self, context: RetrievalContext, limit: int) -> RetrievalContext:
        return RetrievalContext(
            query=context.query,
            results=list(context.results[:limit]),
            memory_hits=list(context.memory_hits),
        )
