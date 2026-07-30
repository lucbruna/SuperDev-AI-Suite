from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

from .planner_metrics import PlannerMetrics
from .planner_queue import PlannerQueue


class PlannerExecutor:
    """Executes plans by running tasks in order respecting dependencies."""

    def __init__(self):
        self.queue = PlannerQueue()
        self.metrics = PlannerMetrics()
        self._executions: dict[str, dict[str, Any]] = {}

    async def execute(self, plan: Any) -> dict[str, Any]:
        plan_id = getattr(plan, "id", "unknown")
        execution = {
            "plan_id": plan_id,
            "status": "running",
            "started_at": datetime.now(UTC).isoformat(),
            "tasks": [],
        }
        self._executions[plan_id] = execution

        tasks = getattr(plan, "tasks", [])
        for task in tasks:
            self.queue.enqueue(task)

        results = []
        while not self.queue.is_empty():
            task = self.queue.dequeue()
            try:
                result = await self._execute_task(task)
                results.append(result)
            except Exception as e:
                results.append({"task": str(task), "error": str(e)})

        execution["status"] = "completed"
        execution["completed_at"] = datetime.now(UTC).isoformat()
        execution["results"] = results
        return execution

    async def _execute_task(self, task: Any) -> dict[str, Any]:
        start = datetime.now(UTC)
        try:
            if asyncio.iscoroutinefunction(task.execute):
                result = await task.execute()
            else:
                result = task.execute()
            self.metrics.record_success()
            return {"task": str(task), "status": "completed", "result": result}
        except Exception as e:
            self.metrics.record_failure()
            return {"task": str(task), "status": "failed", "error": str(e)}
