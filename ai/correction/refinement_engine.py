from __future__ import annotations

from typing import Any


class RefinementEngine:
    """Refines responses to improve quality."""

    def __init__(self) -> None:
        self._rules: list[dict[str, Any]] = []

    def add_rule(self, rule: dict[str, Any]) -> None:
        self._rules.append(rule)

    async def refine(self, response: str, error: dict[str, Any]) -> dict[str, Any]:
        refined = response
        changes = 0
        for rule in self._rules:
            old = rule.get("old", "")
            new = rule.get("new", "")
            if old in refined:
                refined = refined.replace(old, new)
                changes += 1
        return {"success": changes > 0, "corrected": refined, "changes": changes}
