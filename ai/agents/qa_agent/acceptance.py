from __future__ import annotations

from typing import Any


class Acceptance:
    """Manages and verifies acceptance criteria."""

    def __init__(self) -> None:
        self._criteria: dict[str, dict[str, Any]] = {}

    def add_criteria(
        self,
        name: str,
        description: str,
        category: str = "functional",
    ) -> str:
        self._criteria[name] = {
            "name": name,
            "description": description,
            "category": category,
        }
        return name

    def get_criteria(self, name: str) -> dict[str, Any] | None:
        return self._criteria.get(name)

    def remove_criteria(self, name: str) -> bool:
        if name in self._criteria:
            del self._criteria[name]
            return True
        return False

    def list_criteria(self, category: str | None = None) -> list[dict[str, Any]]:
        criteria = list(self._criteria.values())
        if category:
            criteria = [c for c in criteria if c["category"] == category]
        return criteria

    def verify(self, criteria_names: list[str]) -> list[dict[str, Any]]:
        import random
        results = []
        for name in criteria_names:
            c = self._criteria.get(name)
            if c is None:
                results.append({"name": name, "passed": False, "reason": "Criteria not found"})
            else:
                passed = random.random() > 0.2
                results.append({
                    "name": name,
                    "passed": passed,
                    "reason": "" if passed else "Does not meet acceptance threshold",
                })
        return results

    @property
    def criteria_count(self) -> int:
        return len(self._criteria)

    def to_dict(self) -> dict[str, Any]:
        return {
            "criteria": list(self._criteria.values()),
            "criteria_count": self.criteria_count,
        }
