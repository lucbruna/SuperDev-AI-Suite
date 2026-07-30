from __future__ import annotations

from typing import Any


class ChainExecutor:
    """Executes reasoning chains step by step."""

    def __init__(self) -> None:
        self._handlers: dict[str, Any] = {}

    def register_handler(self, step_type: str, handler: Any) -> None:
        self._handlers[step_type] = handler

    async def execute(self, chain: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        steps = chain.get("steps", [])
        results: list[dict[str, Any]] = []
        intermediate: dict[str, Any] = dict(context)
        for step in steps:
            step_type = step.get("type", "reason")
            handler = self._handlers.get(step_type)
            if handler:
                result = await handler(intermediate)
            else:
                result = {"output": f"Executed {step_type}", "status": "completed"}
            results.append({"step": step.get("id"), "result": result})
            intermediate[step.get("id")] = result
        return {"results": results, "final": results[-1]["result"] if results else None}
