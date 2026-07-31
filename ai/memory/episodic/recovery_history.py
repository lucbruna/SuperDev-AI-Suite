from __future__ import annotations

import time
from typing import Any


class RecoveryRecord:
    """A record of a recovery operation."""

    def __init__(
        self,
        recovery_id: str,
        trigger: str,
        status: str,
        actions_taken: list[str],
        details: dict[str, Any] | None = None,
    ):
        self._recovery_id = recovery_id
        self._trigger = trigger
        self._status = status
        self._actions_taken = list(actions_taken)
        self._details = details or {}
        self._timestamp = time.time()

    @property
    def recovery_id(self) -> str:
        return self._recovery_id

    @property
    def trigger(self) -> str:
        return self._trigger

    @property
    def status(self) -> str:
        return self._status

    @property
    def actions_taken(self) -> list[str]:
        return list(self._actions_taken)

    @property
    def details(self) -> dict[str, Any]:
        return dict(self._details)

    @property
    def timestamp(self) -> float:
        return self._timestamp

    def to_dict(self) -> dict[str, Any]:
        return {
            "recovery_id": self._recovery_id,
            "trigger": self._trigger,
            "status": self._status,
            "actions_taken": list(self._actions_taken),
            "timestamp": self._timestamp,
        }


class RecoveryHistory:
    """History of recovery attempts and their outcomes."""

    def __init__(self):
        self._records: list[RecoveryRecord] = []
        self._counter: int = 0

    @property
    def count(self) -> int:
        return len(self._records)

    def record(
        self, trigger: str, status: str, actions_taken: list[str], details: dict[str, Any] | None = None
    ) -> RecoveryRecord:
        self._counter += 1
        rec = RecoveryRecord(f"rec_{self._counter}", trigger, status, actions_taken, details)
        self._records.append(rec)
        return rec

    def get_recent(self, count: int = 50) -> list[RecoveryRecord]:
        return list(self._records[-count:])

    def get_by_status(self, status: str) -> list[RecoveryRecord]:
        return [r for r in self._records if r.status == status]

    def get_successful(self) -> list[RecoveryRecord]:
        return self.get_by_status("success")

    def get_failed(self) -> list[RecoveryRecord]:
        return self.get_by_status("failed")

    def clear(self) -> None:
        self._records.clear()
