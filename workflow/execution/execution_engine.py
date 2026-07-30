from __future__ import annotations

import logging
import time
from typing import Any

from .execution_context import ExecutionContext
from .execution_state import ExecutionState
from .execution_plan import ExecutionPlan
from .execution_history import ExecutionHistory


class ExecutionEngine:
    """Core engine that orchestrates workflow execution."""

    def __init__(self) -> None:
        self._contexts: dict[str, ExecutionContext] = {}
        self._states: dict[str, ExecutionState] = {}
        self._history = ExecutionHistory()
        self._log = logging.getLogger("superdev.workflow.execution.engine")
        self._paused: set[str] = set()

    def execute(self, plan: ExecutionPlan, context: ExecutionContext) -> str:
        exec_id = f"exec_{int(time.time())}"
        self._contexts[exec_id] = context
        self._states[exec_id] = ExecutionState()
        self._log.info("Execution started: %s", exec_id)
        return exec_id

    def pause(self, exec_id: str) -> None:
        self._paused.add(exec_id)
        self._log.info("Execution paused: %s", exec_id)

    def resume(self, exec_id: str) -> None:
        self._paused.discard(exec_id)

    def cancel(self, exec_id: str) -> None:
        self._states.pop(exec_id, None)
        self._contexts.pop(exec_id, None)
        self._paused.discard(exec_id)

    def is_paused(self, exec_id: str) -> bool:
        return exec_id in self._paused

    def get_state(self, exec_id: str) -> ExecutionState | None:
        return self._states.get(exec_id)

    def get_history(self) -> ExecutionHistory:
        return self._history
