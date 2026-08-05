"""AIOS Container Runtime — resource-budgeted execution context.

Conceptual container: runs a target under a declared resource budget
(cpu units, memory, credits). Kept deterministic and in-process; a
real deployment may swap this for process/VM isolation.
"""

from __future__ import annotations

import inspect
from typing import Any

from .runtime import BaseRuntime, RuntimeCallable

DEFAULT_BUDGET = {"cpu": 1.0, "memory_mb": 256.0, "credits": 100.0}


class ContainerRuntime(BaseRuntime):
    """Run targets within a named resource budget."""

    kind = "container"

    def __init__(self, name: str = "container-runtime") -> None:
        super().__init__(name)
        self._allocations: dict[str, dict[str, float]] = {}

    def allocate(self, container_id: str, budget: dict[str, float] | None = None) -> dict[str, float]:
        merged = dict(DEFAULT_BUDGET)
        if budget:
            merged.update(budget)
        self._allocations[container_id] = merged
        return merged

    def release(self, container_id: str) -> None:
        self._allocations.pop(container_id, None)

    async def run(self, target: RuntimeCallable, context: dict[str, Any]) -> dict[str, Any]:
        container_id = context.get("container_id", "default")
        budget = self._allocations.get(container_id, dict(DEFAULT_BUDGET))
        try:
            result = target(context)
            if inspect.isawaitable(result):
                result = await result
            return {"ok": True, "container_id": container_id, "budget": budget, "result": result}
        except Exception as exc:  # noqa: BLE001
            return {
                "ok": False,
                "container_id": container_id,
                "budget": budget,
                "error": f"{type(exc).__name__}: {exc}",
                "result": None,
            }

    def snapshot(self) -> dict[str, Any]:
        return {"allocations": {cid: dict(b) for cid, b in sorted(self._allocations.items())}}
