from __future__ import annotations

from typing import Any, Callable

from .telemetry_event import TelemetryEvent


class TelemetryFilter:
    """Filters telemetry events based on rules."""

    def __init__(self) -> None:
        self._rules: list[Callable[[TelemetryEvent], bool]] = []

    def add_rule(self, rule: Callable[[TelemetryEvent], bool]) -> None:
        self._rules.append(rule)

    def should_record(self, event: TelemetryEvent) -> bool:
        if not self._rules:
            return True
        return all(rule(event) for rule in self._rules)

    def clear(self) -> None:
        self._rules.clear()
