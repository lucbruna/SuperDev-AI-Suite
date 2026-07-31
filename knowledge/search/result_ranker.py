from __future__ import annotations

import logging
from typing import Any

from ..knowledge_models import SearchResult


class ResultRanker:
    """Fuses and ranks results from multiple search strategies."""

    def __init__(self, keyword_weight: float = 0.3, semantic_weight: float = 0.7) -> None:
        self._log = logging.getLogger("superdev.knowledge.search.result_ranker")
        self._keyword_weight = keyword_weight
        self._semantic_weight = semantic_weight

    def fuse(self, keyword_hits: list[SearchResult], semantic_hits: list[SearchResult]) -> list[SearchResult]:
        scores: dict[str, dict[str, Any]] = {}
        for result in keyword_hits:
            entry = scores.setdefault(result.text, {"score": 0.0, "sources": [], "document_id": result.document_id})
            entry["score"] += result.score * self._keyword_weight
            entry["sources"].append("keyword")
        for result in semantic_hits:
            entry = scores.setdefault(result.text, {"score": 0.0, "sources": [], "document_id": result.document_id})
            entry["score"] += result.score * self._semantic_weight
            entry["sources"].append("semantic")
        ranked = sorted(scores.items(), key=lambda pair: pair[1]["score"], reverse=True)
        return [
            SearchResult(
                text=text, score=entry["score"], source="+".join(entry["sources"]),
                document_id=entry["document_id"],
            )
            for text, entry in ranked
        ]

    def top_k(self, results: list[SearchResult], limit: int) -> list[SearchResult]:
        return results[: max(0, limit)]
