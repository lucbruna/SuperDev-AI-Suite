"""Strategy selection for the planner (Volume 31)."""

from __future__ import annotations

from agent_orchestration.orchestrator_models import AgentTask


class StrategyBuilder:
    """Chooses an execution strategy and estimates duration."""

    def build(self, tasks: list[AgentTask]) -> str:
        if not tasks:
            return "single"
        has_dependencies = any(task.dependencies for task in tasks)
        if has_dependencies:
            return "sequential"
        return "parallel" if len(tasks) > 1 else "single"

    def estimate_duration(self, tasks: list[AgentTask],
                          unit: float = 1.0) -> float:
        count = len(tasks)
        if count == 0:
            return 0.0
        if self.build(tasks) == "parallel":
            return unit + max(0, count - 1) * unit * 0.5
        return count * unit
