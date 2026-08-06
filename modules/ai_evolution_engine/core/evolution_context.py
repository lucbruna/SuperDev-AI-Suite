"""Execution context shared by all evolution components."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.ai_evolution_engine.config.evolution_config import EvolutionConfig
from modules.ai_evolution_engine.config.permissions import Permissions
from modules.ai_evolution_engine.core.evolution_events import EvolutionEventBus
from modules.ai_evolution_engine.core.evolution_memory import EvolutionMemory
from modules.ai_evolution_engine.core.evolution_registry import EvolutionRegistry
from modules.ai_evolution_engine.core.evolution_state import EvolutionState


@dataclass(slots=True)
class EvolutionContext:
    """Wiring hub: config, permissions, events, state, memory, registry."""

    config: EvolutionConfig = field(default_factory=EvolutionConfig)
    permissions: Permissions = field(default_factory=Permissions)
    registry: EvolutionRegistry = field(default_factory=EvolutionRegistry)
    events: EvolutionEventBus = field(default_factory=EvolutionEventBus)
    state: EvolutionState = field(default_factory=EvolutionState)
    memory: EvolutionMemory = field(default_factory=EvolutionMemory)
    artifacts: dict[str, object] = field(default_factory=dict)

    def publish(self, event_type: str, payload: dict[str, object] | None = None) -> None:
        self.events.publish(event_type, payload)
        self.state.set_last_event(event_type)

    def set_artifact(self, key: str, value: object) -> None:
        self.artifacts[key] = value

    def get_artifact(self, key: str, default: object = None) -> object:
        return self.artifacts.get(key, default)

    def reset(self) -> None:
        self.state = EvolutionState()
        self.events.clear()
        self.artifacts.clear()
