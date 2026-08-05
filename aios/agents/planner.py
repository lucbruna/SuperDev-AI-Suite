"""PlannerAgent: wraps the planning subsystem to produce executable plans."""
from __future__ import annotations

from typing import Any

from aios.agents.base_agent import BaseAgent
from aios.planning.planner import Planner


class PlannerAgent(BaseAgent):
    def __init__(self, name: str = "planner", planner: Planner | None = None, **kwargs: Any) -> None:
        super().__init__(
            name=name,
            role="planner",
            capabilities=["planning", "scheduling", "decomposition", "optimization"],
            description="Creates executable plans and schedules",
            **kwargs,
        )
        self.planner = planner if planner is not None else Planner()

    def process(self, input_data: Any, context: dict[str, Any]) -> Any:
        if isinstance(input_data, dict):
            goal = str(input_data.get("goal", ""))
            strategy = input_data.get("strategy") or context.get("strategy", "hierarchical")
            subgoals = input_data.get("subgoals") or context.get("subgoals")
        else:
            goal = str(input_data)
            strategy = context.get("strategy", "hierarchical")
            subgoals = context.get("subgoals")
        plan = self.planner.create_plan(
            goal=goal,
            strategy=strategy,
            subgoals=subgoals,
            duration=float(context.get("duration", 1.0)),
        )
        workflow = plan.workflow
        if workflow is None:
            raise RuntimeError(f"plan {plan.plan_id} has no workflow")
        return {
            "plan_id": plan.plan_id,
            "goal": plan.goal,
            "status": plan.status,
            "tasks": [
                {
                    "task_id": t.task_id,
                    "name": t.name,
                    "depends_on": t.depends_on,
                    "duration": t.estimated_duration,
                    "start": t.start_time,
                    "end": t.end_time,
                }
                for t in plan.tasks
            ],
            "order": workflow.order,
            "critical_path": workflow.critical_path,
            "total_duration": workflow.total_duration,
            "schedule": plan.metadata.get("schedule", {}),
        }
