"""Member availability."""

from __future__ import annotations

import time
from typing import Any


class Availability:
    """Tracks whether a member is available, busy or offline."""

    STATUSES = ("available", "busy", "offline")

    def __init__(self, member_id: str,
                 status: str = "available") -> None:
        self.member_id = member_id
        self.status = status if status in self.STATUSES else "available"
        self.updated_at = time.time()

    def set_status(self, status: str) -> bool:
        if status not in self.STATUSES:
            return False
        self.status = status
        self.updated_at = time.time()
        return True

    def to_dict(self) -> dict[str, Any]:
        return {"member_id": self.member_id, "status": self.status,
                "updated_at": self.updated_at}


class AvailabilityManager:
    """Availability registry."""

    def __init__(self) -> None:
        self._states: dict[str, Availability] = {}

    def get(self, member_id: str) -> Availability:
        state = self._states.get(member_id)
        if state is None:
            state = Availability(member_id)
            self._states[member_id] = state
        return state

    def set_status(self, member_id: str, status: str) -> bool:
        return self.get(member_id).set_status(status)

    def available_members(self) -> list[str]:
        return [mid for mid, state in self._states.items()
                if state.status == "available"]

    def summary(self) -> dict[str, int]:
        counts = {status: 0 for status in Availability.STATUSES}
        for state in self._states.values():
            counts[state.status] += 1
        return counts
