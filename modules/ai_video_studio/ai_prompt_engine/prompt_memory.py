"""Prompt memory — store and retrieve past prompts by key."""
from __future__ import annotations

import time
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError


class PromptMemory:
    """In-memory prompt store with recency metadata."""

    def __init__(self, max_entries: int = 200) -> None:
        self._store: dict[str, dict[str, Any]] = {}
        self.max_entries = max_entries

    def save(self, key: str, prompt: str, **meta: Any) -> dict[str, Any]:
        if not key.strip():
            raise ValidationError("Memory key cannot be empty", field="key")
        entry = {"key": key, "prompt": prompt, "created_at": time.time(), **meta}
        self._store[key] = entry
        if len(self._store) > self.max_entries:
            oldest = min(self._store, key=lambda k: self._store[k]["created_at"])
            self._store.pop(oldest, None)
        return entry

    def get(self, key: str) -> dict[str, Any] | None:
        return self._store.get(key)

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        q = query.lower()
        matches = [
            e for e in self._store.values()
            if q in e["prompt"].lower() or q in e["key"].lower()
        ]
        matches.sort(key=lambda e: e["created_at"], reverse=True)
        return matches[:limit]

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def clear(self) -> int:
        count = len(self._store)
        self._store.clear()
        return count

    def size(self) -> int:
        return len(self._store)


_prompt_memory: PromptMemory | None = None


def get_prompt_memory() -> PromptMemory:
    global _prompt_memory
    if _prompt_memory is None:
        _prompt_memory = PromptMemory()
    return _prompt_memory
