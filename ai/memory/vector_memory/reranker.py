from __future__ import annotations

from typing import Any

from .similarity_engine import SimilarityEngine


class Reranker:
    """Re-ranks retrieval results for improved relevance."""

    def __init__(self):
        self._similarity = SimilarityEngine()

    def rerank(self, query_vector: list[float], results: list[Any], weight: float = 0.5) -> list[Any]:
        if not results:
            return results
        scored = []
        for r in results:
            if hasattr(r, "metadata"):
                meta_score = self._metadata_score(r.metadata)
            elif isinstance(r, dict):
                meta_score = self._metadata_score(r.get("metadata", {}))
            else:
                meta_score = 0.0
            sim_score = r.score if hasattr(r, "score") else r.get("score", 0)
            combined = (1 - weight) * sim_score + weight * meta_score
            scored.append((combined, r))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored]

    def _metadata_score(self, metadata: dict[str, Any]) -> float:
        score = 0.0
        if metadata.get("relevance"):
            score += float(metadata["relevance"]) * 0.5
        if metadata.get("importance"):
            score += float(metadata["importance"]) * 0.3
        if metadata.get("recency"):
            score += float(metadata["recency"]) * 0.2
        return score
