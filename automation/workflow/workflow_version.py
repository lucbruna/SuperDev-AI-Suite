"""Semantic versioning of workflow definitions."""

from __future__ import annotations

import logging
import time
from typing import Any


class WorkflowVersion:
    """A single immutable snapshot of a workflow definition."""

    def __init__(self, workflow_id: str, version: str, definition: Any,
                 created_at: float | None = None) -> None:
        self.workflow_id = workflow_id
        self.version = version
        self.definition = definition
        self.created_at = created_at or time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "version": self.version,
            "created_at": self.created_at,
        }


class WorkflowVersioner:
    """Auto-increments and stores workflow versions."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.automation.workflow.version")
        self._versions: dict[str, list[WorkflowVersion]] = {}

    def register(self, definition: Any) -> str:
        """Records a version snapshot and returns its version string."""
        history = self._versions.setdefault(definition.workflow_id, [])
        version = self._next_version(history)
        history.append(WorkflowVersion(definition.workflow_id, version, definition))
        return version

    def version_of(self, workflow_id: str) -> str | None:
        history = self._versions.get(workflow_id, [])
        return history[-1].version if history else None

    def history(self, workflow_id: str) -> list[WorkflowVersion]:
        return list(self._versions.get(workflow_id, []))

    def get(self, workflow_id: str, version: str) -> Any | None:
        for entry in self._versions.get(workflow_id, []):
            if entry.version == version:
                return entry.definition
        return None

    @staticmethod
    def _next_version(history: list[WorkflowVersion]) -> str:
        if not history:
            return "1.0.0"
        current = history[-1].version
        parts = [int(p) for p in current.split(".")]
        parts[2] += 1  # patch bump
        return ".".join(str(p) for p in parts)
