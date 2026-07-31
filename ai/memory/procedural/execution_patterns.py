from __future__ import annotations

from typing import Any


class ExecutionPattern:
    """A reusable execution pattern."""

    def __init__(self, pattern_id: str, name: str, pattern_type: str, steps: list[str], description: str = ""):
        self._pattern_id = pattern_id
        self._name = name
        self._type = pattern_type
        self._steps = list(steps)
        self._description = description

    @property
    def pattern_id(self) -> str:
        return self._pattern_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def pattern_type(self) -> str:
        return self._type

    @property
    def steps(self) -> list[str]:
        return list(self._steps)

    @property
    def description(self) -> str:
        return self._description

    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern_id": self._pattern_id,
            "name": self._name,
            "type": self._type,
            "steps": list(self._steps),
            "description": self._description,
        }


class ExecutionPatterns:
    """Registry of execution patterns."""

    def __init__(self):
        self._patterns: dict[str, ExecutionPattern] = {}

    @property
    def count(self) -> int:
        return len(self._patterns)

    def add(self, pattern: ExecutionPattern) -> None:
        self._patterns[pattern.pattern_id] = pattern

    def get(self, pattern_id: str) -> ExecutionPattern | None:
        return self._patterns.get(pattern_id)

    def get_by_type(self, pattern_type: str) -> list[ExecutionPattern]:
        return [p for p in self._patterns.values() if p.pattern_type == pattern_type]

    def remove(self, pattern_id: str) -> bool:
        return self._patterns.pop(pattern_id, None) is not None

    def clear(self) -> None:
        self._patterns.clear()
