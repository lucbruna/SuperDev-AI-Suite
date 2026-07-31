"""Execution engine for workflows with branching and timeouts."""

from __future__ import annotations

import logging
import time
from typing import Any, Callable

from automation.automation_events import AutomationEventType
from automation.automation_models import WorkflowStatus
from automation.workflow.workflow_state import WorkflowState


class WorkflowExecutor:
    """Runs a workflow definition step-by-step.

    Branching: after a successful step, execution jumps to ``next_on_success``
    when set; after a failed step it jumps to ``next_on_failure`` when set,
    otherwise the workflow fails.
    """

    def __init__(self, actions: dict[str, Callable[[dict[str, Any]], Any]] | None = None,
                 events: Any = None, metrics: Any = None) -> None:
        self._log = logging.getLogger("superdev.automation.workflow.executor")
        self.actions: dict[str, Callable[[dict[str, Any]], Any]] = actions or {}
        self.events = events
        self.metrics = metrics

    def register_action(self, action: str,
                        handler: Callable[[dict[str, Any]], Any]) -> None:
        self.actions[action] = handler

    def run(self, definition: Any,
            initial_vars: dict[str, Any] | None = None) -> WorkflowState:
        state = WorkflowState(definition.workflow_id, initial_vars)
        state.status = WorkflowStatus.RUNNING
        state.started_at = time.time()
        steps = {s.step_id: s for s in definition.steps}
        order = [s.step_id for s in definition.steps]
        visited: set[str] = set()
        index = 0

        self._publish(AutomationEventType.WORKFLOW_STARTED,
                      {"workflow_id": definition.workflow_id})
        if self.metrics is not None:
            self.metrics.increment("workflows.started")

        while 0 <= index < len(order):
            step = steps[order[index]]
            if step.step_id in visited:
                state.error = f"cycle detected at step '{step.step_id}'"
                state.status = WorkflowStatus.FAILED
                self._fail(state)
                break
            visited.add(step.step_id)
            state.current_step_id = step.step_id

            handler = self.actions.get(step.action)
            if handler is None:
                state.error = f"no handler for action: {step.action}"
                state.failed_steps.append(step.step_id)
                self._publish(AutomationEventType.TASK_FAILED,
                              {"step_id": step.step_id, "error": state.error})
                if step.next_on_failure and step.next_on_failure in steps:
                    index = order.index(step.next_on_failure)
                    continue
                state.status = WorkflowStatus.FAILED
                self._fail(state)
                break

            self._publish(AutomationEventType.TASK_STARTED,
                          {"step_id": step.step_id, "action": step.action})
            start = time.monotonic()
            try:
                result = handler(dict(step.params, **state.variables))
                elapsed = time.monotonic() - start
                if step.timeout is not None and elapsed > step.timeout:
                    raise TimeoutError(
                        f"step '{step.step_id}' exceeded timeout of {step.timeout}s")
            except Exception as exc:  # noqa: BLE001
                state.error = str(exc)
                state.failed_steps.append(step.step_id)
                self._publish(AutomationEventType.TASK_FAILED,
                              {"step_id": step.step_id, "error": str(exc)})
                if step.next_on_failure and step.next_on_failure in steps:
                    index = order.index(step.next_on_failure)
                    continue
                state.status = WorkflowStatus.FAILED
                self._fail(state)
                break

            state.step_results[step.step_id] = result
            state.completed_steps.append(step.step_id)
            if isinstance(result, dict):
                state.variables.update(result)
            self._publish(AutomationEventType.TASK_COMPLETED,
                          {"step_id": step.step_id})
            if self.metrics is not None:
                self.metrics.increment("tasks.completed")

            if step.next_on_success and step.next_on_success in steps:
                index = order.index(step.next_on_success)
            else:
                index += 1
        else:
            if state.status is not WorkflowStatus.FAILED:
                state.status = WorkflowStatus.COMPLETED

        if state.status is WorkflowStatus.RUNNING:
            state.status = WorkflowStatus.COMPLETED
        state.finished_at = state.finished_at or time.time()

        if state.status is WorkflowStatus.FAILED:
            self._publish(AutomationEventType.WORKFLOW_FAILED,
                          {"workflow_id": definition.workflow_id,
                           "error": state.error})
        else:
            self._publish(AutomationEventType.WORKFLOW_COMPLETED,
                          {"workflow_id": definition.workflow_id})
        return state

    def _fail(self, state: WorkflowState) -> None:
        if self.metrics is not None:
            self.metrics.increment("workflows.failed")

    def _publish(self, event_type: AutomationEventType,
                 data: dict[str, Any]) -> None:
        if self.events is not None:
            self.events.publish(event_type, data)
