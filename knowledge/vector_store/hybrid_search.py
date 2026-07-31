from __future__ import annotations

import logging
from typing import Any

from ..knowledge_models import Embedding, SearchResult
from .filtering import Filtering
from .ranking import Ranking
from .similarity_search import SimilaritySearch


class HybridSearch:
    """Combines keyword and vector search with weighted fusion."""

    def __init__(self, vector_weight: float = 0.7, keyword_weight: float = 0.3) -> None:
        self._log = logging.getLogger("superdev.knowledge.vector_store.hybrid_search")
        self._vector_weight = vector_weight
        self._keyword_weight = keyword_weight
        self._vector = SimilaritySearch()
        self._ranking = Ranking()
        self._filtering = Filtering()

    def search(self, query: str, query_vector: list[float], texts: list[str],
               vectors: list[list[float]], top_k: int = 5, threshold: float = 0.0) -> list[SearchResult]:
        vector_hits = {
            result.text: result
            for result in self._vector.search(query_vector, [
                Embedding(vector=vector, text=text) for text, vector in zip(texts, vectors)
            ], top_k=top_k * 3, threshold=threshold)
        }
        keyword_hits = self._keyword_rank(query, texts)

        combined: dict[str, float] = {}
        for text, score in keyword_hits.items():
            combined[text] = combined.get(text, 0.0) + score * self._keyword_weight
        for text, result in vector_hits.items():
            combined[text] = combined.get(text, 0.0) + result.score * self._vector_weight

        ranked = sorted(combined.items(), key=lambda pair: pair[1], reverse=True)
        results = []
        for text, score in ranked[:top_k]:
            vector_hit = vector_hits.get(text)
            results.append(
                SearchResult(
                    text=text, score=score, source="hybrid",
                    metadata={
                        "keyword_score": keyword_hits.get(text, 0.0),
                        "vector_score": vector_hit.score if vector_hit is not None else 0.0,
                    },
                )
            )
        return results

    def _keyword_rank(self, query: str, texts: list[str]) -> dict[str, float]:
        query_tokens = set(query.lower().split())
        scores: dict[str, float] = {}
        for text in texts:
            text_tokens = set(text.lower().split())
            if not query_tokens:
                scores[text] = 0.0
                continue
            scores[text] = len(query_tokens & text_tokens) / len(query_tokens)
        return scores
