from __future__ import annotations

from typing import Any


class ExecutionBridge:
    """Bridge between reasoning and the execution engine."""

    def __init__(self) -> None:
        self._handlers: dict[str, Any] = {}

    def register_handler(self, action: str, handler: Any) -> None:
        self._handlers[action] = handler

    async def prepare(self, workflow: dict[str, Any], dependencies: dict[str, Any]) -> dict[str, Any]:
        execution_order: list[str] = []
        nodes = workflow.get("nodes", [])
        resolved: set[str] = set()
        for node in nodes:
            node_id = node.get("node_id", "")
            deps = node.get("dependencies", [])
            if all(d in resolved for d in deps):
                execution_order.append(node_id)
                resolved.add(node_id)
        return {
            "execution_order": execution_order,
            "total": len(execution_order),
            "dependencies": dependencies,
        }
