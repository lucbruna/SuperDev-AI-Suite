"""Execution engine for task orchestration and workflow management."""
from __future__ import annotations

from typing import Any

from .parallel_executor import ParallelExecutor
from .progress_tracker import ProgressTracker
from .task_executor import TaskExecutor
from .workflow_runner import WorkflowRunner


class ExecutionEngine:
    """Central orchestrator for agent task execution and workflow management."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {}
        self._task_executor = TaskExecutor()
        self._workflow_runner = WorkflowRunner()
        self._parallel_executor = ParallelExecutor(
            max_concurrent=self._config.get("max_concurrent", 10)
        )
        self._progress = ProgressTracker()
        self._execution_count: int = 0
        self._error_count: int = 0

    async def execute_task(self, task_id: str, task_spec: dict[str, Any]) -> dict[str, Any]:
        self._execution_count += 1
        self._progress.start(task_id, 1)
        try:
            result = await self._task_executor.execute(task_spec)
            self._progress.complete(task_id)
            return {"task_id": task_id, "status": "completed", "result": result}
        except Exception as e:
            self._error_count += 1
            return {"task_id": task_id, "status": "failed", "error": str(e)}

    async def execute_workflow(self, workflow: dict[str, Any]) -> dict[str, Any]:
        self._execution_count += 1
        wf_id = workflow.get("id", f"wf_{self._execution_count}")
        self._progress.start(wf_id, len(workflow.get("steps", [])))
        result = await self._workflow_runner.run(workflow)
        self._progress.complete(wf_id)
        return {"workflow_id": wf_id, "status": "completed", "result": result}

    def get_execution_status(self, task_id: str) -> dict[str, Any] | None:
        return self._task_executor.get_status(task_id)

    def get_progress(self, operation_id: str) -> dict[str, Any] | None:
        return self._progress.get_progress(operation_id)

    def get_metrics(self) -> dict[str, Any]:
        return {
            "total_executions": self._execution_count,
            "total_errors": self._error_count,
            "success_rate": round(
                (self._execution_count - self._error_count)
                / max(self._execution_count, 1), 2
            ),
            "parallel_queue": self._parallel_executor.get_queue_status(),
        }
