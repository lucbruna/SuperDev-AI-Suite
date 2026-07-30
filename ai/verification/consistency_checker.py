from __future__ import annotations

from typing import Any


class ConsistencyChecker:
    """Checks response consistency against context."""

    def __init__(self) -> None:
        self._rules: list[dict[str, Any]] = []

    def add_rule(self, rule: dict[str, Any]) -> None:
        self._rules.append(rule)

    async def check(self, response: str, context: dict[str, Any]) -> dict[str, Any]:
        issues: list[str] = []
        for rule in self._rules:
            keyword = rule.get("keyword", "")
            if keyword and keyword not in response:
                issues.append(f"Missing expected keyword: {keyword}")
        return {
            "consistent": len(issues) == 0,
            "issues": issues,
            "response_length": len(response),
        }
