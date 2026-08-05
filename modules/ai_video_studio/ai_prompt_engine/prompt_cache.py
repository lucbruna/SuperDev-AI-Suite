"""Prompt cache — LRU cache for prompt processing results."""
from __future__ import annotations

import time
from collections import OrderedDict
from typing import Any


class PromptCache:
    """Simple LRU cache keyed by prompt digest."""

    def __init__(self, capacity: int = 128, ttl_seconds: float = 3600.0) -> None:
        self.capacity = capacity
        self.ttl = ttl_seconds
        self._cache: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    def _key(self, prompt: str) -> str:
        from modules.ai_video_studio.ai_prompt_engine.prompt_embeddings import get_prompt_embeddings

        return get_prompt_embeddings().digest(prompt)

    def get(self, prompt: str) -> Any | None:
        key = self._key(prompt)
        item = self._cache.get(key)
        if item is None:
            return None
        created_at, value = item
        if time.time() - created_at > self.ttl:
            self._cache.pop(key, None)
            return None
        self._cache.move_to_end(key)
        return value

    def set(self, prompt: str, value: Any) -> None:
        key = self._key(prompt)
        self._cache[key] = (time.time(), value)
        self._cache.move_to_end(key)
        while len(self._cache) > self.capacity:
            self._cache.popitem(last=False)

    def has(self, prompt: str) -> bool:
        return self.get(prompt) is not None

    def clear(self) -> int:
        count = len(self._cache)
        self._cache.clear()
        return count

    def size(self) -> int:
        return len(self._cache)


_prompt_cache: PromptCache | None = None


def get_prompt_cache() -> PromptCache:
    global _prompt_cache
    if _prompt_cache is None:
        _prompt_cache = PromptCache()
    return _prompt_cache
