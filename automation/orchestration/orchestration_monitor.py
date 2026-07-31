"""Progress tracking for orchestration plans."""

from __future__ import annotations

from typing import Any

from automation.orchestration.orchestration_models import (OrchestrationPlan,
                                                           TaskStatus)


class OrchestrationMonitor:
    """Records task states and computes plan progress."""

    def __init__(self) -> None:
        self._states: dict[str, TaskStatus] = {}

    def record(self, task: Any) -> None:
        self._states[task.task_id] = task.status

    def status(self, task_id: str) -> TaskStatus | None:
        return self._states.get(task_id)

    def progress(self, plan: OrchestrationPlan) -> dict[str, Any]:
        counts = {status: 0 for status in TaskStatus}
        for task in plan.tasks:
            counts[task.status] += 1
        total = max(len(plan.tasks), 1)
        percent = round(100 * (counts[TaskStatus.COMPLETED] + counts[TaskStatus.FAILED])
                        / total, 1)
        return {
            "plan_id": plan.plan_id,
            "total": len(plan.tasks),
            "completed": counts[TaskStatus.COMPLETED],
            "running": counts[TaskStatus.RUNNING],
            "pending": counts[TaskStatus.PENDING],
            "failed": counts[TaskStatus.FAILED],
            "skipped": counts[TaskStatus.SKIPPED],
            "percent": percent,
        }
