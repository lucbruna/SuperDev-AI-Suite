"""Embeddings layer for intelligence documents."""
from __future__ import annotations

from modules.architecture_intelligence.embeddings.provider import (
    EmbeddingsProvider,
    get_embeddings,
)

__all__ = ["EmbeddingsProvider", "get_embeddings"]
