from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Tuple


class DuplicationDetector:
    """Detects redundant or duplicate memory entries."""

    def __init__(self):
        self._duplicate_count: int = 0
        self._duplicates_log: List[Tuple[str, str]] = []

    @property
    def duplicate_count(self) -> int:
        return self._duplicate_count

    @property
    def duplicates_log(self) -> List[Tuple[str, str]]:
        return list(self._duplicates_log)

    def _content_hash(self, entry: Dict[str, Any]) -> str:
        content = entry.get("content", "")
        if isinstance(content, dict):
            content = str(sorted(content.items()))
        return hashlib.md5(str(content).encode("utf-8")).hexdigest()

    def deduplicate(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen: set = set()
        result: List[Dict[str, Any]] = []
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

    def find_duplicates(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen: Dict[str, List[Dict[str, Any]]] = {}
        for entry in entries:
            h = self._content_hash(entry)
            seen.setdefault(h, []).append(entry)
        return [group[0] for group in seen.values() if len(group) > 1]

    def similarity_score(self, a: Dict[str, Any], b: Dict[str, Any]) -> float:
        keys_a = set(a.keys())
        keys_b = set(b.keys())
        if not keys_a and not keys_b:
            return 1.0
        intersection = keys_a & keys_b
        return len(intersection) / max(len(keys_a | keys_b), 1)

    def clear(self) -> None:
        self._duplicate_count = 0
        self._duplicates_log.clear()
