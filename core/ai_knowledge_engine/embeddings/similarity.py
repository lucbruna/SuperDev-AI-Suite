from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SimilarityResult:
    id: str
    score: float
    vector: Optional[list[float]] = None


class SimilarityCalculator:
    def cosine_similarity(self, a: list[float], b: list[float]) -> float:
        dot = sum(ai * bi for ai, bi in zip(a, b))
        na = math.sqrt(sum(ai * ai for ai in a))
        nb = math.sqrt(sum(bi * bi for bi in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def dot_product(self, a: list[float], b: list[float]) -> float:
        return sum(ai * bi for ai, bi in zip(a, b))

    def euclidean_distance(self, a: list[float], b: list[float]) -> float:
        return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))

    def rank_by_similarity(self, query: list[float], vectors: dict[str, list[float]], top_k: Optional[int] = None) -> list[SimilarityResult]:
        scored: list[SimilarityResult] = []
        for vid, vec in vectors.items():
            score = self.cosine_similarity(query, vec)
            scored.append(SimilarityResult(id=vid, score=score, vector=vec))
        scored.sort(key=lambda x: x.score, reverse=True)
        if top_k is not None:
            scored = scored[:top_k]
        return scored

    def get_most_similar(self, query: list[float], vectors: dict[str, list[float]], n: int = 1) -> list[SimilarityResult]:
        return self.rank_by_similarity(query, vectors, top_k=n)
