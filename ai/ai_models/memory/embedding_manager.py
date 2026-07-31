"""Embedding manager."""

from __future__ import annotations

import hashlib
import time
from typing import Any


class EmbeddingManager:
    def __init__(self, dimension: int = 384) -> None:
        self._embeddings: dict[str, dict[str, Any]] = {}
        self._dimension = dimension

    def create(self, text: str, model: str = "default", metadata: dict[str, Any] = None) -> dict[str, Any]:
        fake_vector = [
            float(int(hashlib.sha256(f"{text}{i}".encode()).hexdigest()[:8], 16)) / 0xFFFFFFFF
            for i in range(self._dimension)
        ]
        entry = {
            "text": text,
            "vector": fake_vector,
            "model": model,
            "metadata": metadata or {},
            "created_at": time.time(),
        }
        key = hashlib.sha256(text.encode()).hexdigest()
        self._embeddings[key] = entry
        return {"key": key, "dimension": self._dimension}

    def get(self, key: str) -> dict[str, Any]:
        return self._embeddings.get(key, {"error": "not_found"})

    def cosine_similarity(self, key1: str, key2: str) -> float:
        e1 = self._embeddings.get(key1, {}).get("vector", [])
        e2 = self._embeddings.get(key2, {}).get("vector", [])
        if not e1 or not e2:
            return 0.0
        dot = sum(a * b for a, b in zip(e1, e2, strict=False))
        norm1 = sum(a * a for a in e1) ** 0.5
        norm2 = sum(b * b for b in e2) ** 0.5
        return dot / (norm1 * norm2) if norm1 and norm2 else 0.0

    def find_similar(self, key: str, top_k: int = 5) -> list[dict[str, Any]]:
        target = self._embeddings.get(key, {}).get("vector", [])
        if not target:
            return []
        similarities = []
        for k, e in self._embeddings.items():
            if k != key:
                sim = self.cosine_similarity(key, k)
                similarities.append({"key": k, "text": e.get("text", ""), "similarity": sim})
        return sorted(similarities, key=lambda x: x["similarity"], reverse=True)[:top_k]

    def delete(self, key: str) -> bool:
        if key in self._embeddings:
            del self._embeddings[key]
            return True
        return False

    def list_all(self) -> list[str]:
        return list(self._embeddings.keys())

    def count(self) -> int:
        return len(self._embeddings)
