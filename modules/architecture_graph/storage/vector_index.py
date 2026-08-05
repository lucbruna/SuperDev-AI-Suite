"""Lightweight vector index over graph nodes.

Pure-Python term-vector index (no numpy/scipy dependency). Every node is
mapped to a sparse feature-hashed vector of fixed dimension; cosine
similarity is computed with plain dict arithmetic. Used for:
* graph search (architecture_graph)
* semantic search / embeddings (architecture_intelligence)
* duplicate detection (similar nodes)
"""
from __future__ import annotations

import hashlib
import re
from typing import Iterable

_TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


def _hash_token(token: str, dim: int) -> tuple[int, int]:
    digest = hashlib.md5(token.encode("utf-8")).digest()
    idx = int.from_bytes(digest[:4], "little") % dim
    sign = 1 if digest[4] & 1 else -1
    return idx, sign


class VectorIndex:
    """Sparse feature-hashed vector index with cosine similarity."""

    def __init__(self, dim: int = 512) -> None:
        self.dim = dim
        self._vectors: dict[str, dict[int, float]] = {}
        self._documents: dict[str, str] = {}

    # --------------------------------------------------------------- building
    @staticmethod
    def tokenize(text: str) -> list[str]:
        return _TOKEN_RE.findall(text.lower())

    def _vector(self, text: str) -> dict[int, float]:
        vec: dict[int, float] = {}
        for token in self.tokenize(text):
            idx, sign = _hash_token(token, self.dim)
            vec[idx] = vec.get(idx, 0.0) + sign
        # Normalize to unit length.
        norm = sum(v * v for v in vec.values()) ** 0.5
        if norm:
            for k in vec:
                vec[k] /= norm
        return vec

    def add(self, doc_id: str, text: str) -> None:
        self._vectors[doc_id] = self._vector(text)
        self._documents[doc_id] = text

    def build(self, documents: Iterable[tuple[str, str]]) -> None:
        for doc_id, text in documents:
            self.add(doc_id, text)

    def clear(self) -> None:
        self._vectors.clear()
        self._documents.clear()

    # ---------------------------------------------------------------- search
    @staticmethod
    def cosine(a: dict[int, float], b: dict[int, float]) -> float:
        if not a or not b:
            return 0.0
        dot = 0.0
        for key, value in a.items():
            other = b.get(key)
            if other is not None:
                dot += value * other
        return dot

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        qv = self._vector(query)
        scored = [
            (doc_id, self.cosine(self._vectors[doc_id], qv))
            for doc_id in self._vectors
        ]
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]

    def similar_to(self, doc_id: str, top_k: int = 10) -> list[tuple[str, float]]:
        """Return the most similar documents to ``doc_id`` (excluding itself)."""
        base = self._vectors.get(doc_id)
        if base is None:
            return []
        scored = [
            (other, self.cosine(self._vectors[other], base))
            for other in self._vectors
            if other != doc_id
        ]
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]

    def similarity(self, a: str, b: str) -> float:
        va = self._vectors.get(a)
        vb = self._vectors.get(b)
        if va is None or vb is None:
            return 0.0
        return self.cosine(va, vb)

    def document(self, doc_id: str) -> str:
        return self._documents.get(doc_id, "")

    @property
    def size(self) -> int:
        return len(self._vectors)

    def __len__(self) -> int:
        return self.size
