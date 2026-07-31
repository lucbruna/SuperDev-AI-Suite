from __future__ import annotations

from typing import Any


class OptimizationPattern:
    """A pattern for optimizing execution."""

    def __init__(self, pattern_id: str, name: str, target: str, technique: str, steps: list[str]):
        self._pattern_id = pattern_id
        self._name = name
        self._target = target
        self._technique = technique
        self._steps = list(steps)

    @property
    def pattern_id(self) -> str:
        return self._pattern_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def target(self) -> str:
        return self._target

    @property
    def technique(self) -> str:
        return self._technique

    @property
    def steps(self) -> list[str]:
        return list(self._steps)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern_id": self._pattern_id,
            "name": self._name,
            "target": self._target,
            "technique": self._technique,
            "steps": list(self._steps),
        }


class OptimizationPatterns:
    """Registry of optimization patterns."""

    def __init__(self):
        self._patterns: dict[str, OptimizationPattern] = {}

    @property
    def count(self) -> int:
        return len(self._patterns)

    def add(self, pattern: OptimizationPattern) -> None:
        self._patterns[pattern.pattern_id] = pattern

    def get(self, pattern_id: str) -> OptimizationPattern | None:
        return self._patterns.get(pattern_id)

    def get_by_target(self, target: str) -> list[OptimizationPattern]:
        return [p for p in self._patterns.values() if p.target == target]

    def remove(self, pattern_id: str) -> bool:
        return self._patterns.pop(pattern_id, None) is not None

    def clear(self) -> None:
        self._patterns.clear()
