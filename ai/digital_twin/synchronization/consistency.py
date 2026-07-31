"""Consistency checker."""

from __future__ import annotations

from typing import Any


class ConsistencyChecker:
    def __init__(self) -> None:
        self._rules: list[dict[str, Any]] = []
        self._violations: list[dict[str, Any]] = []

    def add_rule(self, name: str, check_fn, description: str = "") -> dict[str, Any]:
        rule = {"name": name, "description": description}
        self._rules.append(rule)
        return rule

    def check(self, real_state: dict[str, Any], twin_state: dict[str, Any]) -> dict[str, Any]:
        mismatches = []
        all_keys = set(list(real_state.keys()) + list(twin_state.keys()))
        for key in all_keys:
            real_val = real_state.get(key)
            twin_val = twin_state.get(key)
            if real_val != twin_val:
                mismatches.append({"field": key, "real": real_val, "twin": twin_val})
        consistent = len(mismatches) == 0
        if not consistent:
            self._violations.append({"mismatches": mismatches, "count": len(mismatches)})
        return {"consistent": consistent, "mismatches": mismatches, "total_fields": len(all_keys)}

    def get_violations(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._violations[-limit:]

    def list_rules(self) -> list[dict[str, Any]]:
        return self._rules

    def violation_count(self) -> int:
        return len(self._violations)

    def clear_violations(self) -> int:
        n = len(self._violations)
        self._violations.clear()
        return n
