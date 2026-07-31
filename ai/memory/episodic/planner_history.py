from __future__ import annotations

import time
from typing import Any


class PlanRecord:
    """A record of a planning operation."""

    def __init__(self, plan_id: str, goal: str, status: str, steps: int, details: dict[str, Any] | None = None):
        self._plan_id = plan_id
        self._goal = goal
        self._status = status
        self._steps = steps
        self._details = details or {}
        self._timestamp = time.time()

    @property
    def plan_id(self) -> str:
        return self._plan_id

    @property
    def goal(self) -> str:
        return self._goal

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
            "plan_id": self._plan_id,
            "goal": self._goal,
            "status": self._status,
            "steps": self._steps,
            "timestamp": self._timestamp,
        }


class PlannerHistory:
    """History of planning operations."""

    def __init__(self):
        self._records: list[PlanRecord] = []

    @property
    def count(self) -> int:
        return len(self._records)

    def record(
        self, plan_id: str, goal: str, status: str, steps: int, details: dict[str, Any] | None = None
    ) -> PlanRecord:
        rec = PlanRecord(plan_id, goal, status, steps, details)
        self._records.append(rec)
        return rec

    def get_recent(self, count: int = 50) -> list[PlanRecord]:
        return list(self._records[-count:])

    def get_by_goal(self, goal: str) -> list[PlanRecord]:
        return [r for r in self._records if r.goal == goal]

    def clear(self) -> None:
        self._records.clear()
