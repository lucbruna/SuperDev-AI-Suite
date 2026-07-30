from __future__ import annotations

from typing import Any


class Reranker:
    """Reranks search results using secondary scoring."""

    def rerank(self, query: str, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(results, key=lambda x: x.get("score", 0), reverse=True)
