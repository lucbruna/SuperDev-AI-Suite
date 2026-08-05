"""PlanOptimizer: deterministic plan analysis and optimization recommendations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aios.planning.time_scheduler import TimeScheduler
from aios.planning.workflow_planner import WorkflowPlan


@dataclass
class OptimizationReport:
    objective: str
    actions: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "objective": self.objective,
            "actions": list(self.actions),
            "metrics": dict(self.metrics),
        }


class PlanOptimizer:
    """Read-only optimizer: reports recommendations, never mutates tasks."""

    OBJECTIVES = ("duration", "parallelism")

    def optimize(
        self,
        plan: WorkflowPlan,
        durations: dict[str, float],
        objective: str = "duration",
    ) -> OptimizationReport:
        if objective not in self.OBJECTIVES:
            raise ValueError(f"unknown objective {objective!r}; expected one of {self.OBJECTIVES}")
        durations = {tid: max(0.0, float(durations.get(tid, 1.0))) for tid in plan.order}

        entries = TimeScheduler().schedule(plan.order, plan.dependencies, durations)
        slack = {tid: entry.slack for tid, entry in entries.items()}

        levels: dict[int, int] = {}
        for step in plan.steps:
            levels[step.level] = levels.get(step.level, 0) + 1
        width = max(levels.values(), default=1)

        actions: list[str] = []
        if objective == "duration":
            actions.append(
                f"critical path: {len(plan.critical_path)} task(s) set the total duration ({plan.total_duration:.2f}u)"
            )
            loose = [tid for tid in plan.order if slack[tid] > 0]
            if loose:
                actions.append(f"{len(loose)} task(s) carry slack and can run off the critical path")
            bottleneck = plan.critical_path[-1] if plan.critical_path else None
            actions.append(f"bottleneck: {bottleneck}")
        else:
            actions.append(f"max parallelism width is {width} of {len(plan.order)} task(s)")
            for level in sorted(levels):
                actions.append(f"level {level}: {levels[level]} task(s)")

        metrics: dict[str, Any] = {
            "total_duration": plan.total_duration,
            "tasks": len(plan.order),
            "critical_path_length": len(plan.critical_path),
            "parallelism": round(width / max(1, len(plan.order)), 4),
            "slack_tasks": sum(1 for value in slack.values() if value > 0),
        }
        return OptimizationReport(objective=objective, actions=actions, metrics=metrics)
