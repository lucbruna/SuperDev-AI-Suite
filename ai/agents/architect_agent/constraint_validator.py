from __future__ import annotations

from typing import Any


class ConstraintValidator:
    """Validates architecture designs against defined constraints."""

    def __init__(self) -> None:
        self._constraints: dict[str, dict[str, Any]] = {}

    def add_constraint(
        self,
        name: str,
        description: str,
        category: str = "general",
    ) -> str:
        self._constraints[name] = {
            "name": name,
            "description": description,
            "category": category,
        }
        return name

    def validate(self, architecture: dict[str, Any]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for constraint in self._constraints.values():
            passed = self._check_constraint(constraint, architecture)
            results.append(
                {
                    "constraint": constraint["name"],
                    "category": constraint["category"],
                    "status": "passed" if passed else "failed",
                    "description": constraint["description"],
                }
            )
        if not results:
            results.append(
                {
                    "constraint": "none",
                    "category": "general",
                    "status": "warning",
                    "description": "No constraints defined for validation",
                }
            )
        return results

    def _check_constraint(
        self,
        constraint: dict[str, Any],
        architecture: dict[str, Any],
    ) -> bool:
        name_lower = constraint["name"].lower()
        desc_lower = constraint["description"].lower()
        components = architecture.get("components", [])
        if not components:
            return True

        if "max" in name_lower or "limit" in name_lower:
            max_val = self._extract_number(desc_lower)
            if max_val and len(components) > max_val:
                return False

        if "must have" in desc_lower or "require" in desc_lower:
            required = [w for w in desc_lower.split() if len(w) > 3]
            component_names = [c.get("name", "").lower() for c in components]
            for word in required:
                if word in ("must", "have", "require", "the", "a", "an"):
                    continue
                if not any(word in cn for cn in component_names):
                    return False

        return True

    @staticmethod
    def _extract_number(text: str) -> int | None:
        for word in text.split():
            try:
                return int(word)
            except ValueError:
                continue
        return None

    def remove_constraint(self, name: str) -> bool:
        if name in self._constraints:
            del self._constraints[name]
            return True
        return False

    @property
    def constraint_count(self) -> int:
        return len(self._constraints)

    def to_dict(self) -> dict[str, Any]:
        return {
            "constraints": list(self._constraints.values()),
            "constraint_count": self.constraint_count,
        }
