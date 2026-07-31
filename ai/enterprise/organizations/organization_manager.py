"""Organization manager."""

from __future__ import annotations

from typing import Any


class OrganizationManager:
    def __init__(self) -> None:
        self._memberships: dict[str, list[str]] = {}
        self._settings: dict[str, dict[str, Any]] = {}

    def add_member(self, org_id: str, user_id: str) -> bool:
        self._memberships.setdefault(org_id, [])
        if user_id not in self._memberships[org_id]:
            self._memberships[org_id].append(user_id)
            return True
        return False

    def remove_member(self, org_id: str, user_id: str) -> bool:
        if org_id in self._memberships and user_id in self._memberships[org_id]:
            self._memberships[org_id].remove(user_id)
            return True
        return False

    def get_members(self, org_id: str) -> list[str]:
        return list(self._memberships.get(org_id, []))

    def member_count(self, org_id: str) -> int:
        return len(self._memberships.get(org_id, []))

    def set_setting(self, org_id: str, key: str, value: Any) -> None:
        self._settings.setdefault(org_id, {})[key] = value

    def get_setting(self, org_id: str, key: str, default: Any = None) -> Any:
        return self._settings.get(org_id, {}).get(key, default)

    def get_all_settings(self, org_id: str) -> dict[str, Any]:
        return dict(self._settings.get(org_id, {}))
