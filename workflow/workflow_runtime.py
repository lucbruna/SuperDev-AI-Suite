from __future__ import annotations

import logging
import time
from typing import Any

from .workflow_models import WorkflowDefinition, WorkflowStatus


class WorkflowRuntime:
    """Runtime environment for executing workflows."""

    def __init__(self) -> None:
        self._running: dict[str, WorkflowDefinition] = {}
        self._completed: dict[str, WorkflowDefinition] = {}
        self._log = logging.getLogger("superdev.workflow.runtime")

    def start_workflow(self, definition: WorkflowDefinition) -> None:
        self._running[definition.id] = definition
        definition.status = WorkflowStatus.RUNNING
        self._log.info("Runtime started: %s", definition.id)

    def complete_workflow(self, workflow_id: str) -> None:
        definition = self._running.pop(workflow_id, None)
        if definition:
            definition.status = WorkflowStatus.COMPLETED
            self._completed[workflow_id] = definition

    def fail_workflow(self, workflow_id: str, error: str) -> None:
        definition = self._running.pop(workflow_id, None)
        if definition:
            definition.status = WorkflowStatus.FAILED
            self._completed[workflow_id] = definition

    def is_running(self, workflow_id: str) -> bool:
        return workflow_id in self._running

    def list_running(self) -> list[WorkflowDefinition]:
        return list(self._running.values())

    def list_completed(self) -> list[WorkflowDefinition]:
        return list(self._completed.values())
