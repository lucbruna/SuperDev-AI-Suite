"""Dispatches plan tasks to agents respecting dependencies."""

from __future__ import annotations

from typing import Any

from automation.automation_events import AutomationEventType
from automation.orchestration.orchestration_agent import OrchestrationAgent
from automation.orchestration.orchestration_models import (OrchestrationPlan,
                                                           TaskStatus)
from automation.orchestration.orchestration_monitor import OrchestrationMonitor


class OrchestrationDispatcher:
    """Runs a plan's tasks, honoring dependency order."""

    def __init__(self, monitor: OrchestrationMonitor | None = None,
                 events: Any = None) -> None:
        self.monitor = monitor or OrchestrationMonitor()
        self.events = events

    def dispatch(self, plan: OrchestrationPlan,
                 agents: list[OrchestrationAgent]) -> list[Any]:
        agents_by_id = {a.agent_id: a for a in agents}
        completed: set[str] = set()
        failed: set[str] = set()
        skipped: set[str] = set()

        while len(completed) + len(failed) + len(skipped) < len(plan.tasks):
            progressed = False
            for task in plan.tasks:
                if task.status is not TaskStatus.PENDING:
                    continue
                deps = set(task.depends_on)
                if not deps <= completed:
                    if deps & (failed | skipped):
                        task.status = TaskStatus.SKIPPED
                        skipped.add(task.task_id)
                        self.monitor.record(task)
                        progressed = True
                    continue

                agent = agents_by_id.get(task.agent_id)
                if agent is None:
                    task.status = TaskStatus.FAILED
                    task.error = f"no agent '{task.agent_id}'"
                    failed.add(task.task_id)
                    self.monitor.record(task)
                    progressed = True
                    continue

                task.status = TaskStatus.RUNNING
                self.monitor.record(task)
                self._publish(AutomationEventType.TASK_STARTED,
                              {"task_id": task.task_id, "kind": task.kind})
                try:
                    task.result = agent.execute(task)
                    task.status = TaskStatus.COMPLETED
                    completed.add(task.task_id)
                except Exception as exc:  # noqa: BLE001
                    task.status = TaskStatus.FAILED
                    task.error = str(exc)
                    failed.add(task.task_id)
                    self._publish(AutomationEventType.TASK_FAILED,
                                  {"task_id": task.task_id, "error": str(exc)})
                self.monitor.record(task)
                self._publish(AutomationEventType.TASK_COMPLETED,
                              {"task_id": task.task_id})
                progressed = True

            if not progressed:
                for task in plan.tasks:
                    if task.status is TaskStatus.PENDING:
                        task.status = TaskStatus.SKIPPED
                        self.monitor.record(task)
                break

        plan.status = TaskStatus.COMPLETED if not failed else TaskStatus.FAILED
        return list(plan.tasks)

    def _publish(self, event_type: AutomationEventType,
                 data: dict[str, Any]) -> None:
        if self.events is not None:
            self.events.publish(event_type, data)
