from __future__ import annotations

from typing import Any


class Consolidation:
    """Consolidation of short-term to long-term memory."""

    def __init__(self, min_importance: float = 0.5, batch_size: int = 100):
        self._min_importance = min_importance
        self._batch_size = batch_size
        self._stats: dict[str, int] = {"consolidated": 0, "skipped": 0, "failed": 0}

    @property
    def min_importance(self) -> float:
        return self._min_importance

    @property
    def stats(self) -> dict[str, int]:
        return dict(self._stats)

    def run(self, source: Any, target: Any) -> int:
        count = 0
        entries = self._extract_entries(source)
        for entry in entries:
            if self._should_consolidate(entry):
                try:
                    target.store(entry["key"], entry["data"])
                    count += 1
                    self._stats["consolidated"] += 1
                except Exception:
                    self._stats["failed"] += 1
            else:
                self._stats["skipped"] += 1
        return count

    def _extract_entries(self, source: Any) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        if hasattr(source, "to_dict_list") and callable(source.to_dict_list):
            entries = source.to_dict_list()
        elif hasattr(source, "items") and callable(source.items):
            for key, value in source.items():
                entries.append({"key": str(key), "data": value})
        elif isinstance(source, list):
            for item in source:
                if isinstance(item, dict) and "key" in item:
                    entries.append(item)
        elif isinstance(source, dict):
            for key, value in source.items():
                entries.append({"key": str(key), "data": value})
        return entries[: self._batch_size]

    def _should_consolidate(self, entry: dict[str, Any]) -> bool:
        importance = entry.get("importance", 0.0)
        if isinstance(importance, (int, float)):
            return importance >= self._min_importance
        return True

    def reset_stats(self) -> None:
        self._stats = {"consolidated": 0, "skipped": 0, "failed": 0}
