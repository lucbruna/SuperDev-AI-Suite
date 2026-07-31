from __future__ import annotations

from typing import Any


class WorkflowBridge:
    """Bridge between reasoning and the workflow engine."""

    def __init__(self) -> None:
        self._templates: dict[str, Any] = {}

    def register_template(self, name: str, template: Any) -> None:
        self._templates[name] = template

    async def create_workflow(self, plan: dict[str, Any]) -> dict[str, Any]:
        steps = plan.get("steps", [])
        nodes: list[dict[str, Any]] = []
        for step in steps:
            nodes.append(
                {
                    "node_id": step.get("id"),
                    "type": "action",
                    "config": {"action": step.get("action")},
                    "dependencies": step.get("dependencies", []),
                }
            )
        return {"nodes": nodes, "total_nodes": len(nodes)}

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        plan = context.get("plan", {})
        return await self.create_workflow(plan)
