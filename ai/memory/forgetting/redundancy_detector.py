from __future__ import annotations

from typing import Any


class RedundancyDetector:
    """Detects redundant memory entries based on content overlap."""

    def __init__(self):
        self._redundant_count: int = 0

    @property
    def redundant_count(self) -> int:
        return self._redundant_count

    def find_redundant(self, entries: dict[str, Any]) -> dict[str, Any]:
        redundant: dict[str, Any] = {}
        keys = list(entries.keys())
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                if self._is_redundant(entries[keys[i]], entries[keys[j]]):
                    redundant[keys[j]] = entries[keys[j]]
                    self._redundant_count += 1
        return redundant

    def _is_redundant(self, a: Any, b: Any, threshold: float = 0.8) -> bool:
        if isinstance(a, dict) and isinstance(b, dict):
            return self._dict_overlap(a, b) >= threshold
        return str(a) == str(b)

    def _dict_overlap(self, a: dict[str, Any], b: dict[str, Any]) -> float:
        keys_a = set(a.keys())
        keys_b = set(b.keys())
        if not keys_a or not keys_b:
            return 0.0
        intersection = keys_a & keys_b
        return len(intersection) / max(len(keys_a | keys_b), 1)

    def similarity_matrix(self, entries: dict[str, Any]) -> dict[str, dict[str, float]]:
        matrix: dict[str, dict[str, float]] = {}
        keys = list(entries.keys())
        for k in keys:
            matrix[k] = {}
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                sim = self._dict_overlap(
                    entries[keys[i]] if isinstance(entries[keys[i]], dict) else {},
                    entries[keys[j]] if isinstance(entries[keys[j]], dict) else {},
                )
                matrix[keys[i]][keys[j]] = sim
                matrix[keys[j]][keys[i]] = sim
        return matrix

    def clear(self) -> None:
        self._redundant_count = 0
