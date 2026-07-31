from __future__ import annotations

from typing import Any


class PatternLearning:
    """Learns recurring patterns from data."""

    def __init__(self):
        self._patterns: dict[str, int] = {}
        self._pattern_count: int = 0

    @property
    def patterns(self) -> dict[str, int]:
        return dict(self._patterns)

    @property
    def pattern_count(self) -> int:
        return self._pattern_count

    def learn(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        detected: list[dict[str, Any]] = []
        type_counts: dict[str, int] = {}
        for item in data:
            t = item.get("type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
        for t, count in type_counts.items():
            if count >= 2:
                entry: dict[str, Any] = {"pattern": t, "frequency": count}
                detected.append(entry)
                self._patterns[t] = count
                self._pattern_count += 1
        return detected

    def learn_sequence(self, data: list[str], window: int = 2) -> dict[str, int]:
        sequences: dict[str, int] = {}
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
