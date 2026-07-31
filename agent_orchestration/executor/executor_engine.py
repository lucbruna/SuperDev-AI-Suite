"""Executor subsystem facade (Volume 31)."""

from __future__ import annotations

from typing import Any, Callable

from agent_orchestration.executor.action_manager import ActionManager
from agent_orchestration.executor.command_runner import CommandRunner
from agent_orchestration.executor.task_executor import TaskExecutor
from agent_orchestration.executor.workflow_runner import WorkflowRunner
from agent_orchestration.orchestrator_events import (OrchestratorEvents,
                                                     OrchestratorEventType)
from agent_orchestration.orchestrator_metrics import OrchestratorMetrics
from agent_orchestration.orchestrator_models import (AgentTask, ExecutionResult,
                                                     TaskStatus)
from agent_orchestration.orchestrator_protocols import new_id


class ExecutorEngine:
    """Facade over task, workflow, command and action execution."""

    def __init__(self, events: OrchestratorEvents | None = None,
                 metrics: OrchestratorMetrics | None = None,
                 executor: TaskExecutor | None = None,
                 workflow: WorkflowRunner | None = None,
                 commands: CommandRunner | None = None,
                 actions: ActionManager | None = None) -> None:
        self.events = events or OrchestratorEvents()
        self.metrics = metrics or OrchestratorMetrics()
        self.executor = executor or TaskExecutor()
        self.workflow = workflow or WorkflowRunner(self.executor)
        self.commands = commands or CommandRunner()
        self.actions = actions or ActionManager(self.metrics)

    def execute(self, task: AgentTask) -> ExecutionResult:
        self.events.publish(OrchestratorEventType.TASK_STARTED,
                            {"task_id": task.task_id})
        self.metrics.increment("ao.tasks_started")
        result = self.executor.execute(task)
        event_type = (OrchestratorEventType.TASK_COMPLETED
                      if result.status == TaskStatus.COMPLETED
                      else OrchestratorEventType.TASK_FAILED)
        self.events.publish(event_type, {"task_id": task.task_id,
                                         "status": result.status.value})
        self.metrics.increment("ao.tasks_completed" if result.status
                               == TaskStatus.COMPLETED
                               else "ao.tasks_failed")
        self.metrics.timing("ao.task_duration", result.duration)
        return result

    def run_workflow(self, tasks: list[AgentTask],
                     on_done: Callable[[ExecutionResult], None] | None = None
                     ) -> dict[str, Any]:
        results = (self.workflow.run_then(tasks, on_done) if on_done
                   else self.workflow.run(tasks))
        for result in results:
            self.metrics.increment("ao.workflow_results")
        return self.workflow.summary(results)

    def run_command(self, command: str) -> dict[str, Any]:
        result = self.commands.run(command)
        self.metrics.increment("ao.commands")
        return result

    def register_action(self, name: str, action: Callable[..., Any]) -> None:
        self.actions.register(name, action)

    def execute_action(self, name: str, **params: Any) -> dict[str, Any]:
        return self.actions.execute(name, **params)

    def stats(self) -> dict[str, Any]:
        return {
            "actions": self.actions.stats(),
            "metrics": self.metrics.snapshot(),
        }
