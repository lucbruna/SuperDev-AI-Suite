"""AIOS Rule Engine — forward-chaining rule evaluation.

Rules are callables or (condition, action) dicts. The engine matches
rules against facts and applies actions, iterating until fixpoint
(up to a bounded number of passes).
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable

Rule = Callable[[dict[str, Any]], Any] | dict[str, Any]


class RuleEngine:
    """Forward-chaining rule engine."""

    def __init__(self, max_passes: int = 10) -> None:
        self._rules: list[Rule] = []
        self._max_passes = max_passes

    def add_rule(self, rule: Rule) -> "RuleEngine":
        self._rules.append(rule)
        return self

    def _eval_rule(self, rule: Rule, facts: dict[str, Any]) -> Any:
        if callable(rule):
            return rule(facts)
        condition = rule.get("condition")
        action = rule.get("action")
        if condition is not None and callable(condition) and condition(facts):
            return action(facts) if callable(action) else action
        return None

    def run(self, facts: dict[str, Any]) -> dict[str, Any]:
        """Apply rules until no changes occur (bounded passes)."""
        applied: list[str] = []
        for _pass in range(self._max_passes):
            changed = False
            for index, rule in enumerate(self._rules):
                result = self._eval_rule(rule, facts)
                if isinstance(result, dict):
                    changed = True
                    facts.update(result)
                    applied.append(f"rule-{index}")
            if not changed:
                break
        return {
            "ok": True,
            "facts": facts,
            "rules_applied": applied,
            "passes": _pass + 1,
        }
