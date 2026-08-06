"""Project planner — decomposes a goal into a TaskPlan.

Deterministic, LLM-free decomposition: explicit task specs win when given;
otherwise a single-line goal becomes one task and a multi-line goal becomes
one task per line (when decomposition is enabled). Tasks are topologically
ordered when the config asks for it.
"""
from __future__ import annotations

from typing import Any

from modules.autonomous_developer.config.constants import (
    OP_CREATE,
    PHASE_IMPLEMENT,
    RISK_LOW,
)
from modules.autonomous_developer.config.planner_config import PlannerConfig
from modules.autonomous_developer.core.exceptions import PlanningError
from modules.autonomous_developer.core.models import FileChange, Task, TaskPlan
from modules.autonomous_developer.planner.task_planner import TaskPlanner


class ProjectPlanner:
    """Deterministic goal → TaskPlan decomposition."""

    def __init__(self, config: PlannerConfig | None = None) -> None:
        self.config = config or PlannerConfig()
        self._task_planner = TaskPlanner(config)

    def plan(
        self,
        goal: str,
        *,
        tasks: list[str | dict[str, Any]] | None = None,
        priority: str | None = None,
    ) -> TaskPlan:
        """Build a TaskPlan for ``goal``.

        ``tasks`` may be a list of free-text titles or dict specs (title,
        description, priority, risk, phase, depends_on, files).
        """
        if not goal or not goal.strip():
            raise PlanningError("A goal is required to build a plan", context={"goal": goal})
        resolved_priority = priority or self.config.default_priority
        plan = TaskPlan(goal=goal)
        if tasks is not None:
            for spec in tasks:
                plan.add_task(self._task_from_spec(spec, resolved_priority))
        else:
            lines = [line.strip() for line in goal.splitlines() if line.strip()]
            if self.config.decompose_tasks and len(lines) > 1:
                for line in lines:
                    plan.add_task(self._new_task(line, resolved_priority))
            else:
                plan.add_task(self._new_task(goal.strip(), resolved_priority))
        if len(plan.tasks) > self.config.max_tasks_per_request:
            raise PlanningError(
                f"Goal decomposes to {len(plan.tasks)} tasks "
                f"(max {self.config.max_tasks_per_request})",
                context={"task_count": len(plan.tasks)},
            )
        if self.config.topo_sort:
            plan.tasks = self._task_planner.order_tasks(plan.tasks)
        return plan

    def _new_task(self, title: str, priority: str) -> Task:
        return Task(title=title, priority=priority, phase=PHASE_IMPLEMENT)

    def _task_from_spec(self, spec: str | dict[str, Any], priority: str) -> Task:
        if isinstance(spec, str):
            return self._new_task(spec, priority)
        if not isinstance(spec, dict):
            raise PlanningError(
                f"Unsupported task spec: {type(spec).__name__}", context={"spec": spec}
            )
        title = spec.get("title", "")
        if not title:
            raise PlanningError("Task spec requires a title", context={"spec": spec})
        files: list[FileChange] = []
        for fc in spec.get("files", []):
            if isinstance(fc, FileChange):
                files.append(fc)
            elif isinstance(fc, dict):
                files.append(
                    FileChange(
                        path=fc.get("path", ""),
                        content=fc.get("content"),
                        operation=fc.get("operation", OP_CREATE),
                        old_content=fc.get("old_content"),
                        reason=fc.get("reason", ""),
                    )
                )
        return Task(
            title=title,
            description=spec.get("description", ""),
            priority=spec.get("priority", priority),
            risk=spec.get("risk", RISK_LOW),
            phase=spec.get("phase", ""),
            depends_on=list(spec.get("depends_on", [])),
            files=files,
        )

    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs: Any) -> TaskPlan:
        """Runtime component entry point (registers in the default registry).

        Feeds prior lessons learned from failed runs over the same goal into
        the planning context so the brain avoids repeating past mistakes.
        """
        plan = self.plan(
            goal,
            tasks=kwargs.get("tasks"),
            priority=kwargs.get("priority"),
        )
        lessons = ctx.lessons.for_goal(goal)
        ctx.record("task_count", len(plan.tasks))
        ctx.record("lessons_used", len(lessons))
        ctx.record("knowledge_used", ctx.memory.contains("knowledge_graph"))
        ctx.publish(
            "plan.ready",
            {"goal": plan.goal, "task_count": len(plan.tasks),
             "lessons_used": len(lessons)},
        )
        return plan
