"""Subscription manager."""

from __future__ import annotations


class SubscriptionManager:
    def __init__(self) -> None:
        self._active: dict[str, str] = {}

    def set_active(self, org_id: str, sub_id: str) -> None:
        self._active[org_id] = sub_id

    def get_active(self, org_id: str) -> str | None:
        return self._active.get(org_id)

    def clear_active(self, org_id: str) -> bool:
        if org_id in self._active:
            del self._active[org_id]
            return True
        return False

    def list_active(self) -> dict[str, str]:
        return dict(self._active)

    def count(self) -> int:
        return len(self._active)

    def has_active(self, org_id: str) -> bool:
        return org_id in self._active
