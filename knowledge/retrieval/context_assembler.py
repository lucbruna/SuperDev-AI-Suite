from __future__ import annotations

import logging

from ..knowledge_models import RetrievalContext, SearchResult


class ContextAssembler:
    """Assembles a RetrievalContext from results and memory hits."""

    def __init__(self, max_context_chars: int = 4000) -> None:
        self._log = logging.getLogger("superdev.knowledge.retrieval.context_assembler")
        self.max_context_chars = max_context_chars

    def assemble(self, query: str, results: list[SearchResult],
                 memory_hits: list[str] | None = None) -> RetrievalContext:
        return RetrievalContext(
            query=query,
            results=list(results),
            memory_hits=list(memory_hits or []),
        )

    def truncate(self, context: RetrievalContext, limit: int = 0, chars: int = 0) -> RetrievalContext:
        results = list(context.results)
        if limit > 0:
            results = results[:limit]
        if chars > 0:
            kept = []
            total = 0
            for result in results:
                if total + len(result.text) > chars:
                    break
                kept.append(result)
                total += len(result.text)
            results = kept
        return RetrievalContext(query=context.query, results=results, memory_hits=list(context.memory_hits))
