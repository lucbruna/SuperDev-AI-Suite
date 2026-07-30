from __future__ import annotations

from typing import Any, Dict, List

from .indexing import Indexing
from .storage import Storage


class Optimizer:
    """Optimizer for long-term memory storage patterns."""

    def __init__(self):
        self._stats: Dict[str, int] = {"dedup": 0, "pruned": 0, "reindexed": 0}

    @property
    def stats(self) -> Dict[str, int]:
        return dict(self._stats)

    def run(self, storage: Storage, indexing: Indexing) -> Dict[str, Any]:
        self._stats = {"dedup": 0, "pruned": 0, "reindexed": 0}
        dedup = self._deduplicate(storage)
        pruned = self._prune_empty(storage, indexing)
        reindexed = self._reindex(storage, indexing)
        return {
            "dedup_removed": dedup,
            "pruned": pruned,
            "reindexed": reindexed,
            **self._stats,
        }

    def _deduplicate(self, storage: Storage) -> int:
        seen: set[int] = set()
        removed = 0
        for key in storage.keys():
            data = storage.get(key)
            if data is None:
                continue
            h = hash(str(data))
            if h in seen:
                storage.delete(key)
                removed += 1
                self._stats["dedup"] += 1
            else:
                seen.add(h)
        return removed

    def _prune_empty(self, storage: Storage, indexing: Indexing) -> int:
        pruned = 0
        for key in storage.keys():
            data = storage.get(key)
            if data is None or (isinstance(data, dict) and not data):
                storage.delete(key)
                indexing.remove(key)
                pruned += 1
                self._stats["pruned"] += 1
        return pruned

    def _reindex(self, storage: Storage, indexing: Indexing) -> int:
        count = 0
        for key in storage.keys():
            data = storage.get(key)
            if data and isinstance(data, dict):
                indexing.remove(key)
                indexing.add(key, data)
                count += 1
                self._stats["reindexed"] += 1
        return count

    def reset_stats(self) -> None:
        self._stats = {"dedup": 0, "pruned": 0, "reindexed": 0}
