"""Component registry for the AI Evolution Engine."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class EvolutionRegistry:
    """Registers named components (analyzers, generators, connectors)."""

    _components: dict[str, object] = field(default_factory=dict)

    def register(self, name: str, component: object) -> None:
        self._components[name] = component

    def get(self, name: str, default: object = None) -> object:
        return self._components.get(name, default)

    def names(self) -> list[str]:
        return sorted(self._components)

    def all(self) -> dict[str, object]:
        return dict(self._components)
