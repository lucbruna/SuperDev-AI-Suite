from __future__ import annotations

from typing import Any


class HybridSearch:
    """Combines semantic and lexical search."""

    def __init__(self):
        self._semantic_results: list[dict[str, Any]] = []
        self._lexical_results: list[dict[str, Any]] = []

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        combined: dict[str, dict[str, Any]] = {}
        for r in self._semantic_results + self._lexical_results:
            doc_id = r.get("id", "")
            if doc_id not in combined:
                combined[doc_id] = r
                combined[doc_id]["semantic_score"] = 0.0
                combined[doc_id]["lexical_score"] = 0.0
            combined[doc_id]["semantic_score"] = max(
                combined[doc_id].get("semantic_score", 0), r.get("score", 0)
            )
            combined[doc_id]["lexical_score"] = max(
                combined[doc_id].get("lexical_score", 0), r.get("score", 0)
            )
            combined[doc_id]["score"] = (
                combined[doc_id]["semantic_score"] + combined[doc_id]["lexical_score"]
            ) / 2
        results = sorted(combined.values(), key=lambda x: x.get("score", 0), reverse=True)
        return results[:top_k]
