"""Named action registry for agents (Volume 31)."""

from __future__ import annotations

from typing import Any, Callable

from agent_orchestration.orchestrator_metrics import OrchestratorMetrics

_Action = Callable[..., Any]


class ActionManager:
    """Registers and invokes named agent actions."""

    def __init__(self, metrics: OrchestratorMetrics | None = None) -> None:
        self._actions: dict[str, _Action] = {}
        self.metrics = metrics or OrchestratorMetrics()

    def register(self, name: str, action: _Action) -> None:
        self._actions[name] = action

    def unregister(self, name: str) -> bool:
        return self._actions.pop(name, None) is not None

    def names(self) -> list[str]:
        return list(self._actions)

    def has(self, name: str) -> bool:
        return name in self._actions

    def execute(self, name: str, **params: Any) -> dict[str, Any]:
        action = self._actions.get(name)
        if action is None:
            return {"ok": False, "action": name, "error": "unknown_action"}
        try:
            result = action(**params)
            self.metrics.increment("ao.actions")
            return {"ok": True, "action": name, "data": result}
        except Exception as exc:  # noqa: BLE001 - surface as error dict
            self.metrics.increment("ao.action_errors")
            return {"ok": False, "action": name, "error": str(exc)}

    def stats(self) -> dict[str, Any]:
        counters = self.metrics.snapshot()["counters"]
        return {"actions": len(self._actions),
                "executed": counters.get("ao.actions", 0),
                "errors": counters.get("ao.action_errors", 0)}
