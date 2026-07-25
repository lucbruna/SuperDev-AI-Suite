from __future__ import annotations
import hashlib
import json
from typing import Optional

from ..providers.provider_manager import ProviderManager


class EmbeddingManager:
    def __init__(self):
        self._cache: dict[str, list[float]] = {}

    def _cache_key(self, text: str, model: str = "") -> str:
        raw = f"{text}:{model}"
        return hashlib.sha256(raw.encode()).hexdigest()

    async def embed_texts(self, texts: list[str], provider_name: Optional[str] = None, provider_manager: Optional[ProviderManager] = None) -> list[list[float]]:
        if not texts:
            return []
        provider = None
        if provider_manager and provider_name:
            try:
                provider = provider_manager.get_provider(provider_name)
            except ValueError:
                pass

        results = []
        uncached_texts = []
        uncached_indices = []

        for i, text in enumerate(texts):
            key = self._cache_key(text)
            cached = self._cache.get(key)
            if cached is not None:
                results.append(cached)
            else:
                results.append(None)
                uncached_texts.append(text)
                uncached_indices.append(i)

        if uncached_texts and provider:
            try:
                embeddings = await provider.embeddings(uncached_texts)
                for idx, emb in zip(uncached_indices, embeddings):
                    key = self._cache_key(texts[idx])
                    self._cache[key] = emb
                    results[idx] = emb
            except Exception:
                for idx in uncached_indices:
                    results[idx] = [0.0] * 1536
        else:
            for idx in uncached_indices:
                results[idx] = [0.0] * 1536

        return results

    async def embed_query(self, query: str, provider_name: Optional[str] = None, provider_manager: Optional[ProviderManager] = None) -> list[float]:
        results = await self.embed_texts([query], provider_name, provider_manager)
        return results[0] if results else [0.0] * 1536

    def get_embedding_model(self) -> str:
        return "text-embedding-3-small"

    def clear_cache(self) -> None:
        self._cache.clear()
