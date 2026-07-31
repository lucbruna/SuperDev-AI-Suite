from __future__ import annotations

from typing import Any


class KeywordSearch:
    """Keyword-based search over memory entries."""

    def __init__(self):
        self._search_count: int = 0

    @property
    def search_count(self) -> int:
        return self._search_count

    def search(self, query: str, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        keywords = query.lower().split()
        results: list[tuple] = []
        for entry in entries:
            content = str(entry.get("content", "")).lower()
            score = sum(1 for kw in keywords if kw in content)
            if score > 0:
                results.append((score, entry))
        results.sort(key=lambda x: x[0], reverse=True)
        self._search_count += 1
        return [entry for _, entry in results]

    def search_exact(self, query: str, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        q = query.lower()
        results: list[dict[str, Any]] = []
        for entry in entries:
            content = str(entry.get("content", "")).lower()
            if q in content:
                results.append(entry)
        self._search_count += 1
        return results

    def search_tags(self, tags: list[str], entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        tag_set = set(t.lower() for t in tags)
        results: list[dict[str, Any]] = []
        for entry in entries:
            entry_tags = set(str(t).lower() for t in entry.get("tags", []))
            if tag_set & entry_tags:
                results.append(entry)
        self._search_count += 1
        return results

    def reset(self) -> None:
        self._search_count = 0
