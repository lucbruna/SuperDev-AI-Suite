"""Workflow execution over multiple tasks (Volume 31)."""

from __future__ import annotations

from typing import Any, Callable

from agent_orchestration.executor.task_executor import TaskExecutor
from agent_orchestration.orchestrator_models import (AgentTask, ExecutionResult,
                                                     TaskStatus)
from agent_orchestration.orchestrator_protocols import new_id


class WorkflowRunner:
    """Runs a task list sequentially, honoring dependency order."""

    def __init__(self, executor: TaskExecutor | None = None) -> None:
        self.executor = executor or TaskExecutor()

    def _resolve_order(self, tasks: list[AgentTask]) -> list[AgentTask]:
        remaining = list(tasks)
        done: set[str] = set()
        ordered: list[AgentTask] = []
        while remaining:
            progress = False
            for task in remaining:
                if all(dependency in done
                       for dependency in task.dependencies):
                    ordered.append(task)
                    remaining.remove(task)
                    done.add(task.task_id)
                    progress = True
                    break
            if not progress:
                break  # cycle or missing dependency
        return ordered + remaining

    def run(self, tasks: list[AgentTask]) -> list[ExecutionResult]:
        results: list[ExecutionResult] = []
        for task in self._resolve_order(tasks):
            results.append(self.executor.execute(task))
        return results

    def run_then(self, tasks: list[AgentTask],
                 on_done: Callable[[ExecutionResult], None]) -> list[ExecutionResult]:
        results = self.run(tasks)
        for result in results:
            on_done(result)
        return results

    def summary(self, results: list[ExecutionResult]) -> dict[str, Any]:
        completed = sum(1 for result in results
                        if result.status == TaskStatus.COMPLETED)
        return {"total": len(results), "completed": completed,
                "failed": len(results) - completed,
                "results": [{"task_id": result.task_id,
                             "status": result.status.value,
                             "duration": result.duration}
                            for result in results]}
