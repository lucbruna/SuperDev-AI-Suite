"""Execution engine for pipelines."""

from __future__ import annotations

import logging
import time
from typing import Any, Callable

from automation.automation_events import AutomationEventType
from automation.automation_protocols import new_id
from automation.pipelines.pipeline_models import PipelineRun


class PipelineExecutor:
    """Runs a pipeline definition stage-by-stage.

    On a stage failure: jumps to ``next_on_failure`` when set; otherwise
    ``on_failure == "continue"`` keeps going; otherwise the pipeline fails and
    the remaining stages are marked as skipped.
    """

    def __init__(self, actions: dict[str, Callable[[dict[str, Any]], Any]] | None = None,
                 events: Any = None, metrics: Any = None) -> None:
        self._log = logging.getLogger("superdev.automation.pipelines.executor")
        self.actions: dict[str, Callable[[dict[str, Any]], Any]] = actions or {}
        self.events = events
        self.metrics = metrics

    def register_action(self, action: str,
                        handler: Callable[[dict[str, Any]], Any]) -> None:
        self.actions[action] = handler

    def run(self, definition: Any,
            initial_vars: dict[str, Any] | None = None) -> PipelineRun:
        run = PipelineRun(run_id=new_id("run"), pipeline_id=definition.pipeline_id)
        run.status = "running"
        run.started_at = time.time()
        run.variables = dict(initial_vars or {})
        steps = {s.stage_id: s for s in definition.stages}
        order = [s.stage_id for s in definition.stages]
        visited: set[str] = set()
        index = 0
        failed = False

        self._publish(AutomationEventType.WORKFLOW_STARTED,
                      {"pipeline_id": definition.pipeline_id})

        while 0 <= index < len(order):
            stage = steps[order[index]]
            if failed:
                run.stage_status[stage.stage_id] = "skipped"
                index += 1
                continue
            if stage.stage_id in visited:
                run.error = f"cycle detected at stage '{stage.stage_id}'"
                failed = True
                break
            visited.add(stage.stage_id)
            run.stage_status[stage.stage_id] = "running"

            handler = self.actions.get(stage.action)
            if handler is None:
                run.error = f"no handler for action: {stage.action}"
                run.stage_status[stage.stage_id] = "failed"
                self._publish(AutomationEventType.TASK_FAILED,
                              {"stage_id": stage.stage_id, "error": run.error})
                if stage.next_on_failure and stage.next_on_failure in steps:
                    index = order.index(stage.next_on_failure)
                    continue
                if definition.on_failure == "continue":
                    index += 1
                    continue
                failed = True
                break

            self._publish(AutomationEventType.TASK_STARTED,
                          {"stage_id": stage.stage_id, "action": stage.action})
            start = time.monotonic()
            try:
                result = handler(dict(stage.params, **run.variables))
                elapsed = time.monotonic() - start
                if stage.timeout is not None and elapsed > stage.timeout:
                    raise TimeoutError(
                        f"stage '{stage.stage_id}' exceeded timeout of "
                        f"{stage.timeout}s")
            except Exception as exc:  # noqa: BLE001
                run.error = str(exc)
                run.stage_status[stage.stage_id] = "failed"
                self._publish(AutomationEventType.TASK_FAILED,
                              {"stage_id": stage.stage_id, "error": str(exc)})
                if stage.next_on_failure and stage.next_on_failure in steps:
                    index = order.index(stage.next_on_failure)
                    continue
                if definition.on_failure == "continue":
                    index += 1
                    continue
                failed = True
                break

            run.stage_results[stage.stage_id] = result
            run.stage_status[stage.stage_id] = "completed"
            if isinstance(result, dict):
                run.variables.update(result)
            self._publish(AutomationEventType.TASK_COMPLETED,
                          {"stage_id": stage.stage_id})
            if self.metrics is not None:
                self.metrics.increment("pipeline.stages_completed")

            if stage.next_on_success and stage.next_on_success in steps:
                index = order.index(stage.next_on_success)
            else:
                index += 1

        for stage_id in order:
            run.stage_status.setdefault(stage_id, "skipped")

        run.status = "failed" if failed else "completed"
        run.finished_at = time.time()
        if failed:
            self._publish(AutomationEventType.WORKFLOW_FAILED,
                          {"pipeline_id": definition.pipeline_id,
                           "error": run.error})
        else:
            self._publish(AutomationEventType.WORKFLOW_COMPLETED,
                          {"pipeline_id": definition.pipeline_id})
        return run

    def _publish(self, event_type: AutomationEventType,
                 data: dict[str, Any]) -> None:
        if self.events is not None:
            self.events.publish(event_type, data)
