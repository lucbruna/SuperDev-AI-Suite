"""Agent shutdown management with graceful cleanup."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any


class ShutdownManager:
    """Manages graceful agent shutdown with cleanup hooks."""

    def __init__(self) -> None:
        self._shutdown_hooks: dict[str, list[Callable[..., Any]]] = {}
        self._shutdown_order: list[str] = []
        self._shut_down: dict[str, float] = {}
        self._force_timeout: float = 30.0

    def register_shutdown_hook(self, agent_id: str, hook: Callable[..., Any]) -> None:
        self._shutdown_hooks.setdefault(agent_id, []).append(hook)

    def set_shutdown_order(self, order: list[str]) -> None:
        self._shutdown_order = list(reversed(order))

    def set_force_timeout(self, seconds: float) -> None:
        self._force_timeout = seconds

    async def shutdown_agent(self, agent_id: str) -> dict[str, Any]:
        start = time.time()
        errors: list[str] = []
        for hook in self._shutdown_hooks.get(agent_id, []):
            try:
                result = hook()
                if hasattr(result, "__await__"):
                    await result
            except Exception as e:
                errors.append(str(e))
        self._shut_down[agent_id] = time.time()
        elapsed_ms = round((time.time() - start) * 1000, 2)
        return {
            "agent_id": agent_id,
            "status": "shutdown" if not errors else "partial_shutdown",
            "errors": errors,
            "shutdown_time_ms": elapsed_ms,
        }

    async def shutdown_all(self, agent_ids: list[str] | None = None) -> list[dict[str, Any]]:
        ids = agent_ids or self._shutdown_order
        results: list[dict[str, Any]] = []
        for aid in ids:
            results.append(await self.shutdown_agent(aid))
        return results

    def is_shutdown(self, agent_id: str) -> bool:
        return agent_id in self._shut_down

    def snapshot(self) -> dict[str, Any]:
        return {"shut_down": list(self._shut_down.keys())}
