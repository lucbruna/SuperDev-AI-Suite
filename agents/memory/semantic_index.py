from __future__ import annotations

import hashlib
from typing import Any

from ..base.base_memory import BaseMemory


class SemanticIndex:
    def __init__(self, memory: BaseMemory | None = None, embedding_model: str = "text-embedding-3-small"):
        self._memory = memory
        self._embedding_model = embedding_model
        self._index: dict[str, list[float]] = {}

    def _get_embeddings_from_text(self, text: str) -> list[float]:
        key = hashlib.md5(text.encode()).hexdigest()
        if key in self._index:
            return self._index[key]
        try:
            from openai import OpenAI
            client = OpenAI()
            response = client.embeddings.create(model=self._embedding_model, input=text)
            embedding = response.data[0].embedding
            self._index[key] = embedding
            return embedding
        except ImportError:
            return [0.0] * 1536
        except Exception:
            words = text.lower().split()
            vector = [0.0] * 1536
            for i, word in enumerate(words[:1536]):
                vector[i] = hash(word) % 1000 / 1000.0
            return vector

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(ai * bi for ai, bi in zip(a, b))
        norm_a = sum(ai * ai for ai in a) ** 0.5
        norm_b = sum(bi * bi for bi in b) ** 0.5
        if not norm_a or not norm_b:
            return 0.0
        return dot / (norm_a * norm_b)

    async def index_key(self, key: str, text: str) -> None:
        embedding = self._get_embeddings_from_text(text)
        self._index[f"key:{key}"] = embedding

    async def index_value(self, key: str, value: Any) -> None:
        text = str(value) if not isinstance(value, str) else value
        embedding = self._get_embeddings_from_text(text[:8000])
        self._index[f"val:{key}"] = embedding

    async def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        if not self._index:
            return []

        query_embedding = self._get_embeddings_from_text(query)
        results: list[tuple[str, float]] = []

        for key, embedding in self._index.items():
            score = self._cosine_similarity(query_embedding, embedding)
            results.append((key, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    async def search_with_memory(self, memory: BaseMemory, query: str, top_k: int = 10) -> list[tuple[str, Any, float]]:
        results = await self.search(query, top_k)
        items: list[tuple[str, Any, float]] = []
        for indexed_key, score in results:
            original_key = indexed_key.replace("key:", "").replace("val:", "")
            value = await memory.retrieve(original_key)
            if value is not None:
                items.append((original_key, value, score))
        return items

    async def remove(self, key: str) -> None:
        self._index.pop(f"key:{key}", None)
        self._index.pop(f"val:{key}", None)

    async def clear(self) -> None:
        self._index.clear()

    @property
    def size(self) -> int:
        return len(self._index)