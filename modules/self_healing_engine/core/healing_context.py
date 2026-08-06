"""Execution context shared by every Self-Healing Engine component.

Mirrors the Digital Twin context pattern: ``publish`` for events,
``record`` for stats, artifacts for cross-component data handoff.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.self_healing_engine.config.healing_config import HealingConfig
from modules.self_healing_engine.core.healing_events import HealingEventBus
from modules.self_healing_engine.core.healing_memory import HealingMemory
from modules.self_healing_engine.core.healing_registry import HealingRegistry
from modules.self_healing_engine.core.healing_state import HealingState


@dataclass(slots=True)
class HealingContext:
    """Carries configuration, registry, bus, state, stats and artifacts."""

    config: HealingConfig = field(default_factory=HealingConfig)
    registry: HealingRegistry = field(default_factory=HealingRegistry)
    events: HealingEventBus = field(default_factory=HealingEventBus)
    state: HealingState = field(default_factory=HealingState)
    memory: HealingMemory = field(default_factory=HealingMemory)
    stats: dict[str, object] = field(default_factory=dict)
    artifacts: dict[str, object] = field(default_factory=dict)

    def publish(
        self, event_type: str, payload: dict[str, object] | None = None
    ) -> None:
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
            "memory": len(self.memory),
            "artifacts": sorted(self.artifacts),
        }
