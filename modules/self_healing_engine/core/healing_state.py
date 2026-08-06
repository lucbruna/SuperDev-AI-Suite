"""Typed state store for the Self-Healing Engine."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.self_healing_engine.config.constants import (
    HEALTH_DEGRADED,
    INCIDENT_OPEN,
)


@dataclass(slots=True)
class HealingState:
    """Key/value state store with dirty tracking."""

    _values: dict[str, object] = field(default_factory=dict)
    _dirty: set[str] = field(default_factory=set)

    def set(self, key: str, value: object) -> None:
        self._values[key] = value
        self._dirty.add(key)

    def get(self, key: str, default: object = None) -> object:
        return self._values.get(key, default)

    def delete(self, key: str) -> None:
        if key in self._values:
            del self._values[key]
            self._dirty.add(key)

    def has(self, key: str) -> bool:
        return key in self._values

    def dirty_keys(self) -> set[str]:
        return set(self._dirty)

    def mark_clean(self, key: str | None = None) -> None:
        if key is None:
            self._dirty.clear()
        else:
            self._dirty.discard(key)

    def to_dict(self) -> dict[str, object]:
        return dict(self._values)

    def from_dict(self, values: dict[str, object]) -> None:
        self._values = dict(values)
        self._dirty.clear()

    @property
    def running(self) -> bool:
        return bool(self.get("running", False))

    def set_running(self, running: bool) -> None:
        self.set("running", running)

    @property
    def health_status(self) -> str:
        return str(self.get("health_status", HEALTH_DEGRADED))

    def set_health_status(self, status: str) -> None:
        self.set("health_status", status)

    @property
    def last_health_score(self) -> float:
        value = self.get("health_score", 0.0)
        return float(value) if isinstance(value, (int, float)) else 0.0

    def set_health_score(self, score: float) -> None:
        self.set("health_score", score)

    @property
    def active_incidents(self) -> int:
        value = self.get("active_incidents", 0)
        return int(value) if isinstance(value, (int, float)) else 0

    def set_active_incidents(self, count: int) -> None:
        self.set("active_incidents", count)

    def open_incident(self) -> None:
        self.set("active_incidents", self.active_incidents + 1)
        self.set("incident_status", INCIDENT_OPEN)
