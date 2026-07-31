"""Agent startup management."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any


class StartupManager:
    """Manages agent startup sequence with dependency ordering."""

    def __init__(self) -> None:
        self._startup_order: list[str] = []
        self._startup_hooks: dict[str, list[Callable[..., Any]]] = {}
        self._started_agents: dict[str, float] = {}
        self._startup_errors: dict[str, str] = {}

    def register_startup_hook(self, agent_id: str, hook: Callable[..., Any]) -> None:
        self._startup_hooks.setdefault(agent_id, []).append(hook)

    def set_startup_order(self, order: list[str]) -> None:
        self._startup_order = list(order)

    async def startup_agent(self, agent_id: str) -> dict[str, Any]:
        start = time.time()
        try:
            for hook in self._startup_hooks.get(agent_id, []):
                if callable(hook):
                    result = hook()
                    if hasattr(result, "__await__"):
                        await result
            self._started_agents[agent_id] = time.time()
            return {
                "agent_id": agent_id,
                "status": "started",
                "startup_time_ms": round((time.time() - start) * 1000, 2),
            }
        except Exception as e:
            self._startup_errors[agent_id] = str(e)
            return {"agent_id": agent_id, "status": "error", "error": str(e)}

    async def startup_all(self, agent_ids: list[str] | None = None) -> list[dict[str, Any]]:
        ids = agent_ids or self._startup_order
        results: list[dict[str, Any]] = []
        for aid in ids:
            result = await self.startup_agent(aid)
            results.append(result)
        return results

    def is_started(self, agent_id: str) -> bool:
        return agent_id in self._started_agents

    def get_startup_time(self, agent_id: str) -> float | None:
        return self._started_agents.get(agent_id)

    def get_errors(self) -> dict[str, str]:
        return dict(self._startup_errors)

    def snapshot(self) -> dict[str, Any]:
        return {
            "started": list(self._started_agents.keys()),
            "errors": dict(self._startup_errors),
        }
