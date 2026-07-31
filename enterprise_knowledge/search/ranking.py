"""Result ranking: combine scores and re-rank."""

from __future__ import annotations

from typing import Any


class SearchRanking:
    """Fuses keyword and semantic scores into a single rank."""

    def __init__(self, keyword_weight: float = 0.5,
                 semantic_weight: float = 0.5) -> None:
        total = keyword_weight + semantic_weight or 1.0
        self.keyword_weight = keyword_weight / total
        self.semantic_weight = semantic_weight / total

    def fuse(self, keyword: list[dict[str, Any]],
             semantic: list[dict[str, Any]],
             limit: int = 10) -> list[dict[str, Any]]:
        combined: dict[str, dict[str, Any]] = {}
        for item in keyword:
            key = item.get("id") or item.get("text") or str(id(item))
            combined[key] = {"id": key, "text": item.get("text", ""),
                             "keyword_score": item.get("score", 0.0),
                             "semantic_score": 0.0}
        for item in semantic:
            key = item.get("id") or item.get("text") or str(id(item))
            entry = combined.setdefault(
                key, {"id": key, "text": item.get("text", ""),
                      "keyword_score": 0.0, "semantic_score": 0.0})
            entry["semantic_score"] = item.get("score", 0.0)
        for entry in combined.values():
            entry["score"] = (self.keyword_weight * entry["keyword_score"]
                              + self.semantic_weight * entry["semantic_score"])
        ranked = sorted(combined.values(),
                        key=lambda entry: entry["score"], reverse=True)
        return ranked[:max(0, limit)]

    def rerank(self, results: list[dict[str, Any]],
               context: str = "") -> list[dict[str, Any]]:
        """Bumps results sharing tokens with the query context."""
        if not context:
            return results
        from enterprise_knowledge.knowledge_protocols import tokenize
        terms = set(tokenize(context))
        for item in results:
            text = set(tokenize(item.get("text", "")))
            item["context_bonus"] = len(terms & text) / max(1, len(terms))
            item["score"] = item.get("score", 0.0) * (1 + item["context_bonus"])
        return sorted(results, key=lambda item: item["score"], reverse=True)
