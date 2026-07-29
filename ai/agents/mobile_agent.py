from __future__ import annotations

from typing import Any

from ..base.base_agent import AgentResult, BaseAgent


class MobileAgent(BaseAgent):
    _registry_name = "mobile"

    async def initialize(self) -> None:
        self._status = "ready"

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResult:
        return AgentResult(
            success=True,
            output=f"[MobileAgent] Task received: {task[:100]}",
            metrics={"agent": "mobile", "task_length": len(task)},
        )

    def capabilities(self) -> list[str]:
        return [
            "mobile", "flutter", "swift", "kotlin", "android",
            "ios", "react_native", "app", "cross_platform",
        ]


class PerformanceAgent(BaseAgent):
    _registry_name = "performance"

    async def initialize(self) -> None:
        self._status = "ready"

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResult:
        return AgentResult(
            success=True,
            output=f"[PerformanceAgent] Task received: {task[:100]}",
            metrics={"agent": "performance", "task_length": len(task)},
        )

    def capabilities(self) -> list[str]:
        return [
            "performance", "optimization", "profiling", "benchmark",
            "latency", "throughput", "memory", "cpu", "scalability",
            "load_testing", "bottleneck",
        ]
