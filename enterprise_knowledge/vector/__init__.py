"""Vector memory subsystem (Volume 27, Fase 3)."""

from __future__ import annotations

from .embedding_manager import EmbeddingManager
from .indexing import VectorIndexing
from .retrieval import VectorRetrieval
from .similarity_search import (SimilaritySearch, cosine, dot, euclidean,
                                jaccard)
from .vector_database import VectorDatabase
from .vector_engine import VectorEngine

__all__ = [
    "EmbeddingManager",
    "SimilaritySearch",
    "VectorDatabase",
    "VectorEngine",
    "VectorIndexing",
    "VectorRetrieval",
    "cosine",
    "dot",
    "euclidean",
    "jaccard",
]
