"""Agent activation and deactivation management."""
from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any


class ActivationManager:
    """Manages agent activation and deactivation states."""

    def __init__(self) -> None:
        self._active: dict[str, float] = {}
        self._activation_hooks: dict[str, list[Callable[..., Any]]] = {}
        self._deactivation_hooks: dict[str, list[Callable[..., Any]]] = {}
        self._activation_count: int = 0

    def register_activation_hook(self, agent_id: str, hook: Callable[..., Any]) -> None:
        self._activation_hooks.setdefault(agent_id, []).append(hook)

    def register_deactivation_hook(self, agent_id: str, hook: Callable[..., Any]) -> None:
        self._deactivation_hooks.setdefault(agent_id, []).append(hook)

    async def activate(self, agent_id: str) -> dict[str, Any]:
        start = time.time()
        errors: list[str] = []
        for hook in self._activation_hooks.get(agent_id, []):
            try:
                result = hook()
                if hasattr(result, "__await__"):
                    await result
            except Exception as e:
                errors.append(str(e))
        self._active[agent_id] = time.time()
        self._activation_count += 1
        return {
            "agent_id": agent_id,
            "status": "activated" if not errors else "partial_activation",
            "errors": errors,
            "activation_time_ms": round((time.time() - start) * 1000, 2),
        }

    async def deactivate(self, agent_id: str) -> dict[str, Any]:
        start = time.time()
        errors: list[str] = []
        for hook in self._deactivation_hooks.get(agent_id, []):
            try:
                result = hook()
                if hasattr(result, "__await__"):
                    await result
            except Exception as e:
                errors.append(str(e))
        self._active.pop(agent_id, None)
        return {
            "agent_id": agent_id,
            "status": "deactivated" if not errors else "partial_deactivation",
            "errors": errors,
            "deactivation_time_ms": round((time.time() - start) * 1000, 2),
        }

    def is_active(self, agent_id: str) -> bool:
        return agent_id in self._active

    def get_active_agents(self) -> list[str]:
        return list(self._active.keys())

    def get_activation_count(self) -> int:
        return self._activation_count

    def snapshot(self) -> dict[str, Any]:
        return {
            "active": list(self._active.keys()),
            "total_activations": self._activation_count,
        }
