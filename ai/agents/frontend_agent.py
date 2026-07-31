from __future__ import annotations

from typing import Any

from ..base.base_agent import AgentResult, BaseAgent


class FrontendAgent(BaseAgent):
    _registry_name = "frontend"

    async def initialize(self) -> None:
        self._status = "ready"

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResult:
        return AgentResult(
            success=True,
            output=f"[FrontendAgent] Task received: {task[:100]}",
            metrics={"agent": "frontend", "task_length": len(task)},
        )

    def capabilities(self) -> list[str]:
        return [
            "frontend",
            "react",
            "typescript",
            "ui",
            "component",
            "css",
            "html",
            "nextjs",
            "tailwind",
            "design",
        ]


class UXAgent(BaseAgent):
    _registry_name = "ux_ui"

    async def initialize(self) -> None:
        self._status = "ready"

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResult:
        return AgentResult(
            success=True,
            output=f"[UXAgent] Task received: {task[:100]}",
            metrics={"agent": "ux_ui", "task_length": len(task)},
        )

    def capabilities(self) -> list[str]:
        return [
            "ux",
            "ui",
            "design",
            "usability",
            "accessibility",
            "prototype",
            "wireframe",
            "responsive",
            "interaction",
        ]
