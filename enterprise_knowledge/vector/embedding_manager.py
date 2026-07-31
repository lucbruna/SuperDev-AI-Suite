"""Embedding generation (stdlib-only, deterministic hash embeddings)."""

from __future__ import annotations

import hashlib
import math
from typing import Any

from enterprise_knowledge.knowledge_protocols import tokenize


class EmbeddingManager:
    """Deterministic feature-hash embeddings over word tokens.

    Produces normalized dense vectors so that overlapping texts land
    close together in cosine space (semantic memory building block).
    """

    def __init__(self, dimensions: int = 32) -> None:
        self.dimensions = max(4, int(dimensions))

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in tokenize(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % self.dimensions
            sign = 1.0 if digest[2] % 2 == 0 else -1.0
            vector[index] += sign
        return self._normalize(vector)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]

    def _normalize(self, vector: list[float]) -> list[float]:
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]

    def empty(self) -> list[float]:
        return [0.0] * self.dimensions

    def stats(self) -> dict[str, Any]:
        return {"dimensions": self.dimensions}
