"""AIOS Resource Runtime — quota accounting for platform units.

Tracks consumed/allocated resources (cpu, memory, credits, quota) per
accountable unit, enabling governance limits and capacity planning.
"""

from __future__ import annotations

import inspect
from typing import Any

from .runtime import BaseRuntime, RuntimeCallable


class ResourceRuntime(BaseRuntime):
    """Account resource usage per unit (actor, module, tenant)."""

    kind = "resource"

    def __init__(self, name: str = "resource-runtime") -> None:
        super().__init__(name)
        self._usage: dict[str, dict[str, float]] = {}

    def charge(self, unit: str, **amounts: float) -> dict[str, float]:
        entry = self._usage.setdefault(unit, {})
        for key, value in amounts.items():
            entry[key] = entry.get(key, 0.0) + float(value)
        return dict(entry)

    def usage(self, unit: str) -> dict[str, float]:
        return dict(self._usage.get(unit, {}))

    async def run(self, target: RuntimeCallable, context: dict[str, Any]) -> dict[str, Any]:
        unit = context.get("resource_unit", "anonymous")
        try:
            result = target(context)
            if inspect.isawaitable(result):
                result = await result
            usage = self.charge(unit, executions=1.0)
            return {"ok": True, "resource_unit": unit, "usage": usage, "result": result}
        except Exception as exc:  # noqa: BLE001
            usage = self.charge(unit, executions=1.0, failures=1.0)
            return {
                "ok": False,
                "resource_unit": unit,
                "usage": usage,
                "error": f"{type(exc).__name__}: {exc}",
                "result": None,
            }

    def snapshot(self) -> dict[str, Any]:
        return {"usage": {unit: dict(u) for unit, u in sorted(self._usage.items())}}
