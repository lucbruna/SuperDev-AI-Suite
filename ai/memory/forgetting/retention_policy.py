from __future__ import annotations

import time
from typing import Any


class RetentionPolicy:
    """Defines and enforces retention rules for memory entries."""

    def __init__(self):
        self._max_entries_per_type: dict[str, int] = {}
        self._max_age_per_type: dict[str, float] = {}

    def set_max_entries(self, entry_type: str, max_count: int) -> None:
        self._max_entries_per_type[entry_type] = max_count

    def set_max_age(self, entry_type: str, max_age_seconds: float) -> None:
        self._max_age_per_type[entry_type] = max_age_seconds

    def get_max_entries(self, entry_type: str) -> int | None:
        return self._max_entries_per_type.get(entry_type)

    def get_max_age(self, entry_type: str) -> float | None:
        return self._max_age_per_type.get(entry_type)

    def enforce(self, entries: dict[str, Any]) -> dict[str, Any]:
        kept: dict[str, Any] = {}
        type_groups: dict[str, list] = {}
        for k, v in entries.items():
            t = v.get("type", "unknown") if isinstance(v, dict) else "unknown"
            type_groups.setdefault(t, []).append((k, v))
        for t, group in type_groups.items():
            sorted_group = sorted(
                group,
                key=lambda item: item[1].get("created_at", 0) if isinstance(item[1], dict) else 0,
                reverse=True,
            )
            max_count = self._max_entries_per_type.get(t)
            max_age = self._max_age_per_type.get(t)
            now = time.time()
            for k, v in sorted_group:
                if max_count is not None and len(kept) >= max_count:
                    break
                if max_age is not None:
                    created = v.get("created_at", now) if isinstance(v, dict) else now
                    if now - created > max_age:
                        continue
                kept[k] = v
        return kept

    def clear(self) -> None:
        self._max_entries_per_type.clear()
        self._max_age_per_type.clear()
