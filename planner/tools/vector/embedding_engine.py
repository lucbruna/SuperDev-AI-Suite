from __future__ import annotations

from typing import Any


class EmbeddingEngine:
    """Engine for generating and managing embeddings."""

    def __init__(self, model: str = "text-embedding-3-small", dimension: int = 1536):
        self.model = model
        self.dimension = dimension

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * self.dimension for _ in texts]

    async def embed_query(self, text: str) -> list[float]:
        return [0.0] * self.dimension
