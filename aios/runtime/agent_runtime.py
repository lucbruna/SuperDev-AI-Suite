"""AIOS Agent Runtime — executes agent entries.

Agents expose an ``async run(context) -> dict`` method. The agent
runtime validates the target shape and normalizes outcomes.
"""

from __future__ import annotations

import inspect
from typing import Any

from .runtime import BaseRuntime, RuntimeCallable


class AgentRuntime(BaseRuntime):
    """Execute an agent callable inside the platform runtime."""

    kind = "agent"

    def __init__(self, name: str = "agent-runtime") -> None:
        super().__init__(name)

    async def run(self, target: RuntimeCallable, context: dict[str, Any]) -> dict[str, Any]:
        runner = getattr(target, "run", None)
        if not callable(runner):
            if callable(target):
                runner = target
            else:
                return {
                    "ok": False,
                    "agent_id": context.get("agent_id"),
                    "error": "target is not runnable: no callable 'run'",
                    "result": None,
                }
        result = runner(context)
        if inspect.isawaitable(result):
            result = await result
        if isinstance(result, dict):
            outcome: dict[str, Any] = {"ok": result.pop("ok", True), "result": result}
        else:
            outcome = {"ok": True, "result": result}
        outcome["agent_id"] = context.get("agent_id")
        return outcome
