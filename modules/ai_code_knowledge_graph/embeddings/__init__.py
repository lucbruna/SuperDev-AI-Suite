"""Embeddings package — embedders, vector store and the embedding service."""
from __future__ import annotations

from modules.ai_code_knowledge_graph.embeddings.embedder import Embedder, HashEmbedder
from modules.ai_code_knowledge_graph.embeddings.service import EmbeddingService
from modules.ai_code_knowledge_graph.embeddings.vector_store import (
    MemoryVectorStore,
    PersistentVectorStore,
    VectorStore,
    cosine_similarity,
)

__all__ = [
    "Embedder",
    "EmbeddingService",
    "HashEmbedder",
    "MemoryVectorStore",
    "PersistentVectorStore",
    "VectorStore",
    "cosine_similarity",
]
