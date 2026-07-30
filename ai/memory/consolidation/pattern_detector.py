from __future__ import annotations

from typing import Any, Dict, List


class PatternDetector:
    """Detects recurring patterns in memory entries."""

    def __init__(self):
        self._patterns: Dict[str, int] = {}
        self._pattern_count: int = 0

    @property
    def patterns(self) -> Dict[str, int]:
        return dict(self._patterns)

    @property
    def pattern_count(self) -> int:
        return self._pattern_count

    def detect(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        detected: List[Dict[str, Any]] = []
        type_groups: Dict[str, List[Dict[str, Any]]] = {}
        for entry in entries:
            t = entry.get("type", "unknown")
            type_groups.setdefault(t, []).append(entry)
        for t, group in type_groups.items():
            if len(group) >= 2:
                pattern = {
                    "type": t,
                    "frequency": len(group),
                    "common_keys": self._find_common_keys(group),
                }
                detected.append(pattern)
                key = f"{t}_pattern"
                self._patterns[key] = len(group)
                self._pattern_count += 1
        return detected

    def _find_common_keys(self, entries: List[Dict[str, Any]]) -> List[str]:
        if not entries:
            return []
        common = set(entries[0].keys())
        for entry in entries[1:]:
            common &= set(entry.keys())
        return list(common)

    def detect_sequence(self, entries: List[Dict[str, Any]], window: int = 3) -> List[Dict[str, Any]]:
        sequences: List[Dict[str, Any]] = []
        for i in range(len(entries) - window + 1):
            chunk = entries[i : i + window]
            types = [e.get("type", "?") for e in chunk]
            seq_key = "->".join(types)
            sequences.append({"sequence": seq_key, "position": i, "types": types})
        return sequences

    def clear(self) -> None:
        self._patterns.clear()
        self._pattern_count = 0
