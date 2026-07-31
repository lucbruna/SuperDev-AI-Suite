"""User status."""

from __future__ import annotations


class UserStatusManager:
    def __init__(self) -> None:
        self._statuses: dict[str, str] = {}

    def activate(self, user_id: str) -> bool:
        self._statuses[user_id] = "active"
        return True

    def deactivate(self, user_id: str) -> bool:
        self._statuses[user_id] = "inactive"
        return True

    def suspend(self, user_id: str, reason: str = "") -> bool:
        self._statuses[user_id] = "suspended"
        return True

    def get_status(self, user_id: str) -> str:
        return self._statuses.get(user_id, "active")

    def is_active(self, user_id: str) -> bool:
        return self.get_status(user_id) == "active"

    def list_by_status(self, status: str) -> list:
        return [uid for uid, s in self._statuses.items() if s == status]

    def bulk_update(self, user_ids: list, status: str) -> int:
        count = 0
        for uid in user_ids:
            self._statuses[uid] = status
            count += 1
        return count
