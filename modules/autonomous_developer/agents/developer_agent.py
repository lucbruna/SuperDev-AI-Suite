"""The developer agent: plans, implements and reviews a goal end-to-end."""
from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from modules.autonomous_developer.agents.base import AgentResult, BaseAgent
from modules.autonomous_developer.generator import CodeGenerator
from modules.autonomous_developer.planner import ProjectPlanner
from modules.autonomous_developer.review import CodeReviewer

if TYPE_CHECKING:
    from modules.autonomous_developer.core.context import DeveloperContext

__all__ = ["DeveloperAgent"]

PHASE_PLAN = "plan"


class DeveloperAgent(BaseAgent):
    """Composes the planner, generator and reviewer into one agent run.

    The run stores the produced plan on the context artifact (the same
    convention ``core.runtime`` uses between phases) so the generator can
    pick it up, then asks the reviewer for a verdict on the planned changes.
    """

    name = "developer"
    description = "Plans, implements and reviews a goal end-to-end."

    def run(self, ctx: DeveloperContext, goal: str, **kwargs: Any) -> AgentResult:
        start = time.time()
        try:
            dry_run = bool(kwargs.get("dry_run", False))
            planner = kwargs.get("planner") or ProjectPlanner()
            generator = kwargs.get("generator") or CodeGenerator()
            reviewer = kwargs.get("reviewer") or CodeReviewer()

            plan = planner.run(
                ctx,
                goal,
                tasks=kwargs.get("tasks"),
                priority=kwargs.get("priority"),
            )
            ctx.set_artifact(PHASE_PLAN, plan)
            generation = generator.run(ctx, goal, dry_run=dry_run)

            changes = [change for task in plan.tasks for change in task.files]
            verdict = reviewer.review_changes(
                changes, project_root=ctx.config.project_root
            )

            result = AgentResult(
                agent=self.name,
                goal=goal,
                output=generation.to_dict(),
                artifacts={
                    "plan_id": plan.plan_id,
                    "verdict": verdict.verdict,
                    "files": [change.path for change in changes],
                },
            )
        except Exception as exc:  # noqa: BLE001 - agents surface errors on the result
            result = AgentResult(agent=self.name, goal=goal, error=str(exc))
        result.duration_seconds = round(time.time() - start, 4)
        return result
