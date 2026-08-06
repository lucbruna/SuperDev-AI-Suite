"""Plugin registry: third-party deterministic hooks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext


@dataclass(slots=True)
class EvolutionPlugin:
    """A user-registered hook executed at a pipeline phase."""

    name: str
    phase: str
    enabled: bool = True
    hook: Callable[[EvolutionContext], object] | None = None

    def run(self, ctx: EvolutionContext) -> object:
        if not self.enabled or self.hook is None:
            return None
        return self.hook(ctx)


class PluginRegistry:
    """Registers and dispatches plugins by phase."""

    _PHASES = ("analyze", "learn", "recommend", "forecast", "govern", "plan", "report")

    def __init__(self) -> None:
        self._plugins: dict[str, EvolutionPlugin] = {}

    def register(self, plugin: EvolutionPlugin) -> None:
        if plugin.phase not in self._PHASES:
            raise ValueError(f"unknown phase: {plugin.phase}")
        self._plugins[plugin.name] = plugin

    def unregister(self, name: str) -> None:
        self._plugins.pop(name, None)

    def dispatch(self, phase: str, ctx: EvolutionContext) -> list[object]:
        outputs: list[object] = []
        for name in sorted(self._plugins):
            plugin = self._plugins[name]
            if plugin.phase == phase and plugin.enabled:
                outputs.append(plugin.run(ctx))
        return outputs
