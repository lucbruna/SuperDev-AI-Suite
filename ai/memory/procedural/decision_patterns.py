from __future__ import annotations

from typing import Any


class DecisionPattern:
    """A pattern for making decisions."""

    def __init__(
        self, pattern_id: str, name: str, decision_type: str, criteria: list[str], rules: dict[str, Any] | None = None
    ):
        self._pattern_id = pattern_id
        self._name = name
        self._type = decision_type
        self._criteria = list(criteria)
        self._rules = rules or {}

    @property
    def pattern_id(self) -> str:
        return self._pattern_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def decision_type(self) -> str:
        return self._type

    @property
    def criteria(self) -> list[str]:
        return list(self._criteria)

    @property
    def rules(self) -> dict[str, Any]:
        return dict(self._rules)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern_id": self._pattern_id,
            "name": self._name,
            "type": self._type,
            "criteria": list(self._criteria),
            "rules": dict(self._rules),
        }


class DecisionPatterns:
    """Registry of decision patterns."""

    def __init__(self):
        self._patterns: dict[str, DecisionPattern] = {}

    @property
    def count(self) -> int:
        return len(self._patterns)

    def add(self, pattern: DecisionPattern) -> None:
        self._patterns[pattern.pattern_id] = pattern

    def get(self, pattern_id: str) -> DecisionPattern | None:
        return self._patterns.get(pattern_id)

    def get_by_type(self, decision_type: str) -> list[DecisionPattern]:
        return [p for p in self._patterns.values() if p.decision_type == decision_type]

    def remove(self, pattern_id: str) -> bool:
        return self._patterns.pop(pattern_id, None) is not None

    def clear(self) -> None:
        self._patterns.clear()
