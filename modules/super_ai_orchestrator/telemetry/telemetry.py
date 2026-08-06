"""Telemetry — deterministic counters and gauges.

Counters only ever increase via ``inc``; gauges are set explicitly via
``set``. ``snapshot()`` returns a stable, ordered dict. No clock, no I/O.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Telemetry:
    """Counter/gauge store.

    Attributes:
        counters: name -> integer count.
        gauges: name -> numeric value.
    """

    counters: dict[str, int] = field(default_factory=dict)
    gauges: dict[str, float] = field(default_factory=dict)

    def inc(self, name: str, amount: int = 1) -> int:
        self.counters[name] = self.counters.get(name, 0) + amount
        return self.counters[name]

    def count(self, name: str) -> int:
        return self.counters.get(name, 0)

    def set(self, name: str, value: float) -> float:
        self.gauges[name] = float(value)
        return self.gauges[name]

    def gauge(self, name: str) -> float:
        return self.gauges.get(name, 0.0)

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(sorted(self.counters.items())),
            "gauges": dict(sorted(self.gauges.items())),
        }

    def reset(self) -> None:
        self.counters.clear()
        self.gauges.clear()
