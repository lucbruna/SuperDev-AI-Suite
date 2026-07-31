from __future__ import annotations

from typing import Any

from .storage import Storage


class Retrieval:
    """Retrieval strategies for long-term memory."""

    def __init__(self, storage: Storage):
        self._storage = storage

    def exact_match(self, key: str) -> Any | None:
        return self._storage.get(key)

    def batch_retrieve(self, keys: list[str]) -> dict[str, Any]:
        return {k: self._storage.get(k) for k in keys if self._storage.has(k)}

    def prefix_search(self, prefix: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for key in self._storage:
            if key.startswith(prefix):
                data = self._storage.get(key)
                if data:
                    results.append({"key": key, "data": data})
        return results

    def keyword_search(self, keyword: str) -> list[dict[str, Any]]:
        kw = keyword.lower()
        results: list[dict[str, Any]] = []
        for key in self._storage:
            if kw in key.lower():
                data = self._storage.get(key)
                if data:
                    results.append({"key": key, "data": data})
        return results
