from __future__ import annotations

import time
from typing import Any


class ExecutionRecord:
    """A record of a single execution."""

    def __init__(self, execution_id: str, action: str, status: str, details: dict[str, Any] | None = None):
        self._execution_id = execution_id
        self._action = action
        self._status = status
        self._details = details or {}
        self._timestamp = time.time()

    @property
    def execution_id(self) -> str:
        return self._execution_id

    @property
    def action(self) -> str:
        return self._action

    @property
    def status(self) -> str:
        return self._status

    @property
    def details(self) -> dict[str, Any]:
        return dict(self._details)

    @property
    def timestamp(self) -> float:
        return self._timestamp

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_id": self._execution_id,
            "action": self._action,
            "status": self._status,
            "details": dict(self._details),
            "timestamp": self._timestamp,
        }


class ExecutionHistory:
    """History of actions executed by the system."""

    def __init__(self):
        self._records: list[ExecutionRecord] = []
        self._counter: int = 0

    @property
    def count(self) -> int:
        return len(self._records)

    def record(self, action: str, status: str, details: dict[str, Any] | None = None) -> ExecutionRecord:
        self._counter += 1
        rec = ExecutionRecord(f"exec_{self._counter}", action, status, details)
        self._records.append(rec)
        return rec

    def get_recent(self, count: int = 50) -> list[ExecutionRecord]:
        return list(self._records[-count:])

    def get_by_action(self, action: str) -> list[ExecutionRecord]:
        return [r for r in self._records if r.action == action]

    def get_by_status(self, status: str) -> list[ExecutionRecord]:
        return [r for r in self._records if r.status == status]

    def clear(self) -> None:
        self._records.clear()
