from __future__ import annotations

import hashlib
from typing import Any


class DuplicationDetector:
    """Detects redundant or duplicate memory entries."""

    def __init__(self):
        self._duplicate_count: int = 0
        self._duplicates_log: list[tuple[str, str]] = []

    @property
    def duplicate_count(self) -> int:
        return self._duplicate_count

    @property
    def duplicates_log(self) -> list[tuple[str, str]]:
        return list(self._duplicates_log)

    def _content_hash(self, entry: dict[str, Any]) -> str:
        content = entry.get("content", "")
        if isinstance(content, dict):
            content = str(sorted(content.items()))
        return hashlib.md5(str(content).encode("utf-8")).hexdigest()

    def deduplicate(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set = set()
        result: list[dict[str, Any]] = []
        self._duplicates_log.clear()
        for entry in entries:
            h = self._content_hash(entry)
            if h in seen:
                self._duplicates_log.append((entry.get("id", "?"), h))
                self._duplicate_count += 1
            else:
                seen.add(h)
                result.append(entry)
        return result

    def find_duplicates(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: dict[str, list[dict[str, Any]]] = {}
        for entry in entries:
            h = self._content_hash(entry)
            seen.setdefault(h, []).append(entry)
        return [group[0] for group in seen.values() if len(group) > 1]

    def similarity_score(self, a: dict[str, Any], b: dict[str, Any]) -> float:
        keys_a = set(a.keys())
        keys_b = set(b.keys())
        if not keys_a and not keys_b:
            return 1.0
        intersection = keys_a & keys_b
        return len(intersection) / max(len(keys_a | keys_b), 1)

    def clear(self) -> None:
        self._duplicate_count = 0
        self._duplicates_log.clear()
