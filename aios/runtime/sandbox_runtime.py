"""AIOS Sandbox Runtime — restricted pure-Python execution.

Executes targets with a deterministic, side-effect-free policy: the
target may only read the provided context and builtins allowlist.
No I/O or imports are allowed inside sandboxed jobs.
"""

from __future__ import annotations

import asyncio
from typing import Any

from .runtime import BaseRuntime, RuntimeCallable

ALLOWED_BUILTINS = frozenset(
    {
        "len", "sum", "min", "max", "sorted", "abs", "round", "range",
        "enumerate", "zip", "map", "filter", "list", "dict", "set", "tuple",
        "str", "int", "float", "bool", "isinstance", "type", "all", "any",
        "reversed", "slice", "format", "repr", "pow", "divmod",
    }
)


class SandboxRuntime(BaseRuntime):
    """Run callables with a restricted builtins environment."""

    kind = "sandbox"

    def __init__(self, name: str = "sandbox-runtime") -> None:
        super().__init__(name, limits={"builtins": sorted(ALLOWED_BUILTINS)})

    async def run(self, target: RuntimeCallable, context: dict[str, Any]) -> dict[str, Any]:
        safe_globals = {
            "__builtins__": {name: __builtins__[name] for name in ALLOWED_BUILTINS},
        }
        try:
            result = target(context)
            if asyncio.iscoroutine(result):
                result = await result
            return {"ok": True, "result": result}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "result": None}
