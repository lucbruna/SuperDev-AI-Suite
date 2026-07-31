from __future__ import annotations

import logging

from ..indexing.index_manager import IndexManager
from ..knowledge_models import SearchResult


class KeywordSearch:
    """Search over the keyword inverted index."""

    def __init__(self, index_manager: IndexManager | None = None) -> None:
        self._log = logging.getLogger("superdev.knowledge.search.keyword_search")
        self.index_manager = index_manager or IndexManager()

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        hits = self.index_manager.keyword.search(query)
        results = []
        for document_id, score in hits[:top_k]:
            results.append(
                SearchResult(
                    text=document_id,
                    score=score,
                    source="keyword",
                    document_id=document_id,
                    metadata=self.index_manager.metadata.get(document_id),
                )
            )
        return results
