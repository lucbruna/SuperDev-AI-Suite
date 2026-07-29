from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class SearchResult:
    id: str
    score: float
    metadata: Optional[dict[str, Any]] = None


class SimilaritySearch:
    def __init__(self) -> None:
        self._vectors: dict[str, list[float]] = {}
        self._texts: dict[str, str] = {}
        self._metadata: dict[str, dict[str, Any]] = {}

    def search(self, query_vector: list[float], top_k: int = 10) -> list[SearchResult]:
        scored: list[SearchResult] = []
        for vid, vec in self._vectors.items():
            score = self.get_similarity_score(query_vector, vec)
            scored.append(SearchResult(id=vid, score=score, metadata=self._metadata.get(vid)))
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]

    def search_by_vector(self, vector: list[float], top_k: int = 10) -> list[SearchResult]:
        return self.search(vector, top_k)

    def search_by_text(self, text: str, top_k: int = 10) -> list[SearchResult]:
        query_tokens = set(text.lower().split())
        scored: list[SearchResult] = []
        for vid, stored_text in self._texts.items():
            stored_tokens = set(stored_text.lower().split())
            overlap = len(query_tokens & stored_tokens)
            total = len(query_tokens | stored_tokens)
            score = overlap / total if total > 0 else 0.0
            scored.append(SearchResult(id=vid, score=score, metadata=self._metadata.get(vid)))
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]

    def rank_results(self, results: list[SearchResult]) -> list[SearchResult]:
        return sorted(results, key=lambda x: x.score, reverse=True)

    def get_similarity_score(self, a: list[float], b: list[float]) -> float:
        dot = sum(ai * bi for ai, bi in zip(a, b))
        na = math.sqrt(sum(ai * ai for ai in a))
        nb = math.sqrt(sum(bi * bi for bi in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def add_vector(self, vid: str, vector: list[float], text: str = "", metadata: Optional[dict[str, Any]] = None) -> None:
        self._vectors[vid] = vector
        if text:
            self._texts[vid] = text
        if metadata:
            self._metadata[vid] = metadata
