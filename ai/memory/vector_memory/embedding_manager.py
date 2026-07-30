from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional

from .cache import Cache
from .embedding_repository import EmbeddingRepository


class EmbeddingManager:
    """Manages embedding life cycle — generation, caching, delegation."""

    def __init__(self, repository: Optional[EmbeddingRepository] = None, cache: Optional[Cache] = None):
        self._repository = repository or EmbeddingRepository()
        self._cache = cache or Cache()
        self._dimension: int = 0

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def total_embeddings(self) -> int:
        return self._repository.count

    def _content_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def embed(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[float]:
        cached = self._cache.get(content)
        if cached is not None:
            return cached
        vector = self._generate(content)
        if not self._dimension:
            self._dimension = len(vector)
        vector_id = self._content_hash(content)
        self._repository.store(vector_id, vector, metadata or {})
        self._cache.set(content, vector)
        return vector

    def embed_batch(self, items: List[Tuple[str, Dict[str, Any]]]) -> List[List[float]]:
        return [self.embed(content, meta) for content, meta in items]

    def _generate(self, content: str) -> List[float]:
        """Deterministic pseudo-embedding from content hash for baseline use."""
        h = hashlib.sha256(content.encode("utf-8")).digest()
        vec = [b / 255.0 for b in h]
        norm = sum(x * x for x in vec) ** 0.5
        if norm > 0:
            vec = [x / norm for x in vec]
        if self._dimension:
            vec = vec[: self._dimension]
        return vec

    def clear_cache(self) -> None:
        self._cache.clear()
