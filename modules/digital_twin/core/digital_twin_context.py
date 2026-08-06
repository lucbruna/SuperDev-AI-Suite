"""Execution context shared by every Digital Twin component.

Mirrors the Autonomous Developer context pattern: ``publish`` for events,
``record`` for stats, artifacts for cross-component data handoff.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.digital_twin.config.digital_twin_config import DigitalTwinConfig
from modules.digital_twin.core.digital_twin_events import TwinEventBus
from modules.digital_twin.core.digital_twin_registry import TwinRegistry
from modules.digital_twin.core.digital_twin_state import TwinState


@dataclass(slots=True)
class DigitalTwinContext:
    """Carries configuration, registry, bus, state, stats and artifacts."""

    config: DigitalTwinConfig = field(default_factory=DigitalTwinConfig)
    registry: TwinRegistry = field(default_factory=TwinRegistry)
    events: TwinEventBus = field(default_factory=TwinEventBus)
    state: TwinState = field(default_factory=TwinState)
    stats: dict[str, object] = field(default_factory=dict)
    artifacts: dict[str, object] = field(default_factory=dict)

    def publish(self, event_type: str, payload: dict[str, object] | None = None) -> None:
        self.events.publish(event_type, payload)

    def record(self, key: str, value: object) -> None:
        self.stats[key] = value

    def increment(self, key: str, by: int = 1) -> None:
        current = self.stats.get(key, 0)
        self.stats[key] = (int(current) if isinstance(current, int) else 0) + by

    def set_artifact(self, name: str, value: object) -> None:
        self.artifacts[name] = value

    def get_artifact(self, name: str, default: object = None) -> object:
        return self.artifacts.get(name, default)

    def summary(self) -> dict[str, object]:
        return {
            "stats": dict(self.stats),
            "state": self.state.to_dict(),
            "events": len(self.events.history()),
            "artifacts": sorted(self.artifacts),
        }
