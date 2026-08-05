"""Embeddings provider for intelligence documents.

Wraps the Architecture Graph module's deterministic embedder; optionally swaps
in an API-backed embedding model when configured. Deterministic fallback keeps
RAG working without external services.
"""
from __future__ import annotations

from typing import Any


class EmbeddingsProvider:
    """Adapter over the graph module embedder (heuristic default)."""

    def __init__(self, provider: Any | None = None) -> None:
        self._provider = provider

    @property
    def available(self) -> bool:
        return True

    def embed(self, text: str) -> dict[int, float]:
        """Return a sparse bag-of-words vector as {hash: weight}."""
        if self._provider is not None:
            dense = self._provider.embed(text)
            if isinstance(dense, list):
                return {i: float(v) for i, v in enumerate(dense) if v}
        from modules.architecture_graph.ai.architecture_embeddings import Embeddings

        return Embeddings().embed(text)

    def dense(self, text: str) -> list[float]:
        """Return a dense vector (for providers that support it)."""
        if self._provider is not None:
            dense = self._provider.embed(text)
            if isinstance(dense, list):
                return dense
        return []


def get_embeddings() -> EmbeddingsProvider:
    return EmbeddingsProvider()
