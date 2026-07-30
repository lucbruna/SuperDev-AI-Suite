from __future__ import annotations

from typing import Any, Dict, List


class PatternLearning:
    """Learns recurring patterns from data."""

    def __init__(self):
        self._patterns: Dict[str, int] = {}
        self._pattern_count: int = 0

    @property
    def patterns(self) -> Dict[str, int]:
        return dict(self._patterns)

    @property
    def pattern_count(self) -> int:
        return self._pattern_count

    def learn(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        detected: List[Dict[str, Any]] = []
        type_counts: Dict[str, int] = {}
        for item in data:
            t = item.get("type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
        for t, count in type_counts.items():
            if count >= 2:
                entry: Dict[str, Any] = {"pattern": t, "frequency": count}
                detected.append(entry)
                self._patterns[t] = count
                self._pattern_count += 1
        return detected

    def learn_sequence(self, data: List[str], window: int = 2) -> Dict[str, int]:
        sequences: Dict[str, int] = {}
        for i in range(len(data) - window + 1):
            seq = "->".join(data[i : i + window])
            sequences[seq] = sequences.get(seq, 0) + 1
        for seq, count in sequences.items():
            self._patterns[seq] = count
            self._pattern_count += 1
        return sequences

    def clear(self) -> None:
        self._patterns.clear()
        self._pattern_count = 0
