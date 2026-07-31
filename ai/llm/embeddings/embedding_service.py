from __future__ import annotations

import math
from typing import Any

from .embedding_provider import EmbeddingProviderInterface


class EmbeddingService:
    """Service for embedding operations and similarity search."""

    def __init__(self, provider: EmbeddingProviderInterface | None = None) -> None:
        self._provider = provider

    @property
    def provider(self) -> EmbeddingProviderInterface | None:
        return self._provider

    def set_provider(self, provider: EmbeddingProviderInterface) -> None:
        self._provider = provider

    async def embed(self, text: str) -> list[float]:
        if self._provider is None:
            raise RuntimeError("No embedding provider configured")
        return await self._provider.embed(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if self._provider is None:
            raise RuntimeError("No embedding provider configured")
        return await self._provider.embed_batch(texts)

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float:
        if len(a) != len(b):
            raise ValueError("Vector dimension mismatch")
        dot = sum(x * y for x, y in zip(a, b, strict=False))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    async def search(
        self,
        query: str,
        corpus: list[str],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        query_vec = await self.embed(query)
        corpus_vecs = await self.embed_batch(corpus)

        scored: list[tuple[float, int, str]] = []
        for i, text in enumerate(corpus):
            sim = self.cosine_similarity(query_vec, corpus_vecs[i])
            scored.append((sim, i, text))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {"score": round(s, 4), "index": i, "text": t}
            for s, i, t in scored[:top_k]
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "has_provider": self._provider is not None,
            "provider": self._provider.to_dict() if self._provider else None,
        }
