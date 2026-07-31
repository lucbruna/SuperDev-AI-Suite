from __future__ import annotations

import time
from typing import Any


class WorkflowRecord:
    """A record of a workflow execution."""

    def __init__(self, workflow_id: str, name: str, status: str, steps: int, details: dict[str, Any] | None = None):
        self._workflow_id = workflow_id
        self._name = name
        self._status = status
        self._steps = steps
        self._details = details or {}
        self._timestamp = time.time()

    @property
    def workflow_id(self) -> str:
        return self._workflow_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def status(self) -> str:
        return self._status

    @property
    def steps(self) -> int:
        return self._steps

    @property
    def details(self) -> dict[str, Any]:
        return dict(self._details)

    @property
    def timestamp(self) -> float:
        return self._timestamp

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self._workflow_id,
            "name": self._name,
            "status": self._status,
            "steps": self._steps,
            "timestamp": self._timestamp,
        }


class WorkflowHistory:
    """History of workflow executions."""

    def __init__(self):
        self._records: list[WorkflowRecord] = []

    @property
    def count(self) -> int:
        return len(self._records)

    def record(self, workflow_id: str, name: str, status: str, steps: int, details: dict[str, Any] | None = None) -> WorkflowRecord:
        rec = WorkflowRecord(workflow_id, name, status, steps, details)
        self._records.append(rec)
        return rec

    def get_recent(self, count: int = 50) -> list[WorkflowRecord]:
        return list(self._records[-count:])

    def get_by_status(self, status: str) -> list[WorkflowRecord]:
        return [r for r in self._records if r.status == status]

    def clear(self) -> None:
        self._records.clear()
