from __future__ import annotations

from typing import Any, Dict, List, Optional

from .storage import Storage


class Retrieval:
    """Retrieval strategies for long-term memory."""

    def __init__(self, storage: Storage):
        self._storage = storage

    def exact_match(self, key: str) -> Any | None:
        return self._storage.get(key)

    def batch_retrieve(self, keys: List[str]) -> Dict[str, Any]:
        return {k: self._storage.get(k) for k in keys if self._storage.has(k)}

    def prefix_search(self, prefix: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for key in self._storage.keys():
            if key.startswith(prefix):
                data = self._storage.get(key)
                if data:
                    results.append({"key": key, "data": data})
        return results

    def keyword_search(self, keyword: str) -> List[Dict[str, Any]]:
        kw = keyword.lower()
        results: List[Dict[str, Any]] = []
        for key in self._storage.keys():
            if kw in key.lower():
                data = self._storage.get(key)
                if data:
                    results.append({"key": key, "data": data})
        return results
