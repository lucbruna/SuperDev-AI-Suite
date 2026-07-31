from __future__ import annotations

import logging

from ..knowledge_models import SearchResult


class CitationManager:
    """Assigns numeric citations to deduplicated sources."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.rag.citation_manager")
        self._sources: dict[str, SearchResult] = {}
        self._order: list[str] = []

    def register(self, results: list[SearchResult]) -> None:
        for result in results:
            key = result.document_id or result.text
            if key not in self._sources:
                self._sources[key] = result
                self._order.append(key)

    def format_sources(self) -> list[str]:
        formatted: list[str] = []
        for index, key in enumerate(self._order, start=1):
            result = self._sources[key]
            snippet = result.text[:60].replace("\n", " ")
            formatted.append(f"{index}. {snippet} (score={result.score:.2f})")
        return formatted

    def cite(self, result: SearchResult) -> str:
        key = result.document_id or result.text
        if key not in self._sources:
            return ""
        return f"[{self._order.index(key) + 1}]"
