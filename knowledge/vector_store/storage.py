from __future__ import annotations

import logging
import threading
from typing import Any

from ..knowledge_interfaces import VectorStore
from ..knowledge_models import Embedding, SearchResult
from ..embeddings.similarity import Similarity


class InMemoryVectorStorage(VectorStore):
    """Thread-safe in-memory vector store with cosine similarity search."""

    def __init__(self, threshold: float = 0.0) -> None:
        self._log = logging.getLogger("superdev.knowledge.vector_store.storage")
        self._items: dict[str, Embedding] = {}
        self._threshold = threshold
        self._lock = threading.RLock()
        self._next_id = 1

    def add(self, embedding: Embedding) -> str:
        with self._lock:
            embedding_id = f"vec-{self._next_id}"
            self._next_id += 1
            self._items[embedding_id] = embedding
            return embedding_id

    def search(self, query_vector: list[float], top_k: int = 5) -> list[SearchResult]:
        with self._lock:
            scored: list[tuple[float, Embedding]] = []
            for embedding in self._items.values():
                score = Similarity.cosine(query_vector, embedding.vector)
                if score >= self._threshold:
                    scored.append((score, embedding))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            SearchResult(
                text=embedding.text,
                score=score,
                source=embedding.metadata.get("source", "vector"),
                document_id=embedding.document_id,
                metadata=dict(embedding.metadata),
            )
            for score, embedding in scored[:top_k]
        ]

    def delete(self, embedding_id: str) -> bool:
        with self._lock:
            return self._items.pop(embedding_id, None) is not None

    def count(self) -> int:
        with self._lock:
            return len(self._items)

    def get(self, embedding_id: str) -> Embedding | None:
        with self._lock:
            return self._items.get(embedding_id)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def to_dict(self) -> dict[str, Any]:
        with self._lock:
            return {eid: emb.to_dict() for eid, emb in self._items.items()}

    def load_dict(self, data: dict[str, dict[str, Any]]) -> None:
        with self._lock:
            self._items = {eid: Embedding(**item) for eid, item in data.items()}
