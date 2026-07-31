"""Event routing rules."""

from __future__ import annotations

from typing import Any


class EventRouter:
    """Maps event types to fan-out targets using exact and wildcard rules."""

    def __init__(self) -> None:
        self._rules: list[tuple[str, str]] = []  # (pattern, target)

    def add_rule(self, pattern: str, target: str) -> None:
        self._rules.append((pattern, target))

    def route(self, event_type: str) -> list[str]:
        targets: list[str] = []
        for pattern, target in self._rules:
            if pattern == "*" or pattern == event_type:
                targets.append(target)
            elif pattern.endswith("*") and event_type.startswith(pattern[:-1]):
                targets.append(target)
        return sorted(set(targets))

    def clear(self) -> None:
        self._rules.clear()

    def rules(self) -> list[dict[str, str]]:
        return [{"pattern": p, "target": t} for p, t in self._rules]
