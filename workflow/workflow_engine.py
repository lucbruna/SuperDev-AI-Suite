from __future__ import annotations

import logging
import time
from typing import Any

from .workflow_models import (
    WorkflowDefinition,
    WorkflowStatus,
    WorkflowStep,
    StepStatus,
)
from .workflow_config import WorkflowConfig
from .workflow_context import WorkflowContext
from .workflow_state import WorkflowStateManager
from .workflow_events import WorkflowEvents
from .workflow_metrics import WorkflowMetrics
from .workflow_logger import WorkflowLogger
from .workflow_registry import WorkflowRegistry
from .workflow_interfaces import IWorkflowEngine


class WorkflowEngine(IWorkflowEngine):
    """Core workflow engine orchestrating execution."""

    def __init__(
        self,
        config: WorkflowConfig | None = None,
        registry: WorkflowRegistry | None = None,
    ) -> None:
        self._config = config or WorkflowConfig()
        self._registry = registry or WorkflowRegistry()
        self._contexts: dict[str, WorkflowContext] = {}
        self._states: dict[str, WorkflowStateManager] = {}
        self._events = WorkflowEvents()
        self._metrics = WorkflowMetrics()
        self._logger = WorkflowLogger("workflow.engine")
        self._log = logging.getLogger("superdev.workflow.engine")

    def create(self, definition: WorkflowDefinition) -> str:
        wf_id = definition.id or f"wf_{int(time.time())}"
        definition.id = wf_id
        definition.created_at = time.time()
        definition.updated_at = time.time()
        self._registry.register(wf_id, definition)
        self._events.emit("workflow.created", {"id": wf_id})
        self._log.info("Workflow created: %s", wf_id)
        return wf_id

    def start(self, workflow_id: str) -> None:
        definition = self._registry.get(workflow_id)
        if not definition:
            raise ValueError(f"Workflow not found: {workflow_id}")

        definition.status = WorkflowStatus.RUNNING
        definition.updated_at = time.time()
        ctx = WorkflowContext(workflow_id=workflow_id)
        state = WorkflowStateManager(workflow_id=workflow_id)
        self._contexts[workflow_id] = ctx
        self._states[workflow_id] = state
        self._events.emit("workflow.started", {"id": workflow_id})
        self._log.info("Workflow started: %s", workflow_id)

    def pause(self, workflow_id: str) -> None:
        definition = self._registry.get(workflow_id)
        if definition:
            definition.status = WorkflowStatus.PAUSED
            definition.updated_at = time.time()
        self._events.emit("workflow.paused", {"id": workflow_id})

    def cancel(self, workflow_id: str) -> None:
        definition = self._registry.get(workflow_id)
        if definition:
            definition.status = WorkflowStatus.CANCELLED
            definition.updated_at = time.time()
        self._events.emit("workflow.cancelled", {"id": workflow_id})

    def get_status(self, workflow_id: str) -> WorkflowStatus:
        definition = self._registry.get(workflow_id)
        if not definition:
            return WorkflowStatus.DRAFT
        return definition.status

    def get_context(self, workflow_id: str) -> WorkflowContext | None:
        return self._contexts.get(workflow_id)

    def get_state(self, workflow_id: str) -> WorkflowStateManager | None:
        return self._states.get(workflow_id)

    @property
    def events(self) -> WorkflowEvents:
        return self._events

    @property
    def metrics(self) -> WorkflowMetrics:
        return self._metrics
