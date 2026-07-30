from __future__ import annotations

from typing import Any


class SimulationRunner:
    """Runs simulation scenarios and collects results."""

    def __init__(self) -> None:
        self._plugins: dict[str, Any] = {}

    def register_plugin(self, name: str, plugin: Any) -> None:
        self._plugins[name] = plugin

    async def run(self, scenario: dict[str, Any]) -> dict[str, Any]:
        steps = scenario.get("steps", [])
        executed = 0
        failures = 0
        for step in steps:
            try:
                plugin = self._plugins.get(step.get("type", "default"))
                if plugin:
                    await plugin(step)
                executed += 1
            except Exception:
                failures += 1
        return {
            "total_steps": len(steps),
            "executed": executed,
            "failures": failures,
            "success_rate": executed / len(steps) if steps else 1.0,
        }
