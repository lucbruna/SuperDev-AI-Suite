"""Rule engine for decision making (Volume 31)."""

from __future__ import annotations

from typing import Any, Callable

_Condition = Callable[[dict[str, Any]], bool]
_Action = Callable[[dict[str, Any]], Any]


class RuleEngine:
    """Evaluates ordered if-then rules against a context dict."""

    def __init__(self) -> None:
        self._rules: list[dict[str, Any]] = []

    def add_rule(self, name: str, condition: _Condition,
                 action: _Action) -> None:
        self._rules.append({"name": name, "condition": condition,
                            "action": action})

    def evaluate(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        fired: list[dict[str, Any]] = []
        for rule in self._rules:
            try:
                if rule["condition"](context):
                    result = rule["action"](context)
                    fired.append({"rule": rule["name"], "ok": True,
                                  "result": result})
            except Exception as exc:  # noqa: BLE001 - isolate rules
                fired.append({"rule": rule["name"], "ok": False,
                              "error": str(exc)})
        return fired

    def count(self) -> int:
        return len(self._rules)

    def names(self) -> list[str]:
        return [rule["name"] for rule in self._rules]
