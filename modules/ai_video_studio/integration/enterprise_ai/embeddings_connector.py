"""Embeddings Connector — deterministic hash-based vectors (no ML dependencies)."""
from __future__ import annotations

import hashlib
import math
from typing import Any

DIM = 64


def _token_hash(token: str, dim: int) -> int:
    return int(hashlib.md5(token.encode("utf-8")).hexdigest()[:8], 16) % dim


class EmbeddingsConnector:
    """Produces fixed-size deterministic embedding vectors from text."""

    def embed(self, text: str, *, dim: int = DIM) -> dict[str, Any]:
        vector = [0.0] * dim
        for token in text.lower().split():
            vector[_token_hash(token, dim)] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        vector = [round(v / norm, 6) for v in vector]
        return {"vector": vector, "dim": dim, "tokens": len(text.split())}


_embeddings_connector: EmbeddingsConnector | None = None


def get_embeddings_connector() -> EmbeddingsConnector:
    global _embeddings_connector
    if _embeddings_connector is None:
        _embeddings_connector = EmbeddingsConnector()
    return _embeddings_connector
