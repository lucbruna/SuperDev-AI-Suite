"""Runtime state for the AI Evolution Engine (deterministic)."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class EvolutionState:
    """Mutable state owned by a single context instance."""

    _values: dict[str, object] = field(default_factory=dict)
    _dirty: set[str] = field(default_factory=set)

    @property
    def running(self) -> bool:
        return bool(self._values.get("running", False))

    def set_running(self, running: bool) -> None:
        self._values["running"] = running
        self._dirty.add("running")

    @property
    def cycles(self) -> int:
        return int(self._values.get("cycles", 0))

    def increment_cycles(self, amount: int = 1) -> None:
        self._values["cycles"] = self.cycles + amount
        self._dirty.add("cycles")

    @property
    def last_analysis_score(self) -> float:
        return float(self._values.get("last_analysis_score", 0.0))

    def set_last_analysis_score(self, score: float) -> None:
        self._values["last_analysis_score"] = score
        self._dirty.add("last_analysis_score")

    @property
    def open_recommendations(self) -> int:
        return int(self._values.get("open_recommendations", 0))

    def set_open_recommendations(self, count: int) -> None:
        self._values["open_recommendations"] = count
        self._dirty.add("open_recommendations")

    @property
    def open_decisions(self) -> int:
        return int(self._values.get("open_decisions", 0))

    def set_open_decisions(self, count: int) -> None:
        self._values["open_decisions"] = count
        self._dirty.add("open_decisions")

    @property
    def last_event(self) -> str:
        return str(self._values.get("last_event", ""))

    def set_last_event(self, event_type: str) -> None:
        self._values["last_event"] = event_type
        self._dirty.add("last_event")

    def set(self, key: str, value: object) -> None:
        self._values[key] = value
        self._dirty.add(key)

    def get(self, key: str, default: object = None) -> object:
        return self._values.get(key, default)

    def snapshot(self) -> dict[str, object]:
        return dict(self._values)

    def dirty(self) -> set[str]:
        return set(self._dirty)

    def clear_dirty(self) -> None:
        self._dirty.clear()
