from __future__ import annotations

from typing import Any


class Search:
    """Base search over memory entries."""

    def __init__(self):
        self._search_count: int = 0

    @property
    def search_count(self) -> int:
        return self._search_count

    def search(self, query: str, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        q = query.lower()
        results: list[dict[str, Any]] = []
        for entry in entries:
            content = str(entry.get("content", ""))
            if q in content.lower():
                results.append(entry)
        self._search_count += 1
        return results

    def search_fields(self, query: str, entries: list[dict[str, Any]], fields: list[str]) -> list[dict[str, Any]]:
        q = query.lower()
        results: list[dict[str, Any]] = []
        for entry in entries:
            for field in fields:
                val = str(entry.get(field, ""))
                if q in val.lower():
                    results.append(entry)
                    break
        self._search_count += 1
        return results

    def reset(self) -> None:
        self._search_count = 0
