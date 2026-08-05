"""Pattern learning — detects recurring patterns in productions."""
from __future__ import annotations



class PatternLearning:
    """Counts recurring decision patterns."""

    def __init__(self) -> None:
        self._patterns: dict[str, int] = {}

    def record(self, pattern: str) -> None:
        self._patterns[pattern] = self._patterns.get(pattern, 0) + 1

    def top(self, limit: int = 5) -> list[tuple[str, int]]:
        return sorted(self._patterns.items(), key=lambda item: item[1], reverse=True)[:limit]


_pattern_learning: PatternLearning | None = None


def get_pattern_learning() -> PatternLearning:
    global _pattern_learning
    if _pattern_learning is None:
        _pattern_learning = PatternLearning()
    return _pattern_learning
