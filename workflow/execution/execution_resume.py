from __future__ import annotations

import logging
from typing import Any


class ExecutionResumer:
    """Handles resumption of failed or paused executions."""

    def __init__(self) -> None:
        self._checkpoints: dict[str, dict[str, Any]] = {}
        self._log = logging.getLogger("superdev.workflow.execution.resume")

    def save_checkpoint(self, exec_id: str, state: dict[str, Any]) -> None:
        self._checkpoints[exec_id] = state
        self._log.info("Checkpoint saved for %s", exec_id)

    def find_checkpoint(self, exec_id: str) -> dict[str, Any] | None:
        return self._checkpoints.get(exec_id)

    def restore_state(self, exec_id: str) -> dict[str, Any] | None:
        return self._checkpoints.pop(exec_id, None)

    def list_checkpoints(self) -> list[str]:
        return list(self._checkpoints.keys())
