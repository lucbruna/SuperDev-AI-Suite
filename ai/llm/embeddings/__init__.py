from __future__ import annotations

"""Embedding generation and similarity search."""

from .embedding_provider import EmbeddingProviderInterface
from .embedding_service import EmbeddingService

__all__ = [
    "EmbeddingProviderInterface",
    "EmbeddingService",
]
