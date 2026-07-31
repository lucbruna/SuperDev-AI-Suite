"""Task execution for a single agent (Volume 31)."""

from __future__ import annotations

import time
from typing import Any, Callable

from agent_orchestration.orchestrator_models import (AgentTask, ExecutionResult,
                                                     TaskStatus)
from agent_orchestration.orchestrator_protocols import new_id

_Runner = Callable[[AgentTask], Any]


class TaskExecutor:
    """Runs a task through an injected runner and wraps the outcome."""

    def __init__(self, runner: _Runner | None = None) -> None:
        self.runner = runner or self._default_runner

    def _default_runner(self, task: AgentTask) -> Any:
        return f"ok:{task.title}"

    def execute(self, task: AgentTask) -> ExecutionResult:
        started = time.monotonic()
        try:
            output = self.runner(task)
            status = TaskStatus.COMPLETED
            error = ""
        except Exception as exc:  # noqa: BLE001 - wrap any failure
            output = None
            status = TaskStatus.FAILED
            error = str(exc)
        duration = time.monotonic() - started
        task.attempts += 1
        task.result = output
        task.error = error
        task.status = status
        return ExecutionResult(
            result_id=new_id("result"), task_id=task.task_id,
            agent_id=task.agent_id, status=status, output=output,
            error=error, duration=duration)
