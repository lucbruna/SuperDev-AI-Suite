"""Departments."""

from __future__ import annotations

import time
from typing import Any


class DepartmentManager:
    def __init__(self) -> None:
        self._departments: dict[str, dict[str, Any]] = {}

    def create(self, org_id: str, name: str, description: str = "", parent_id: str = "") -> dict[str, Any]:
        import uuid

        dept_id = str(uuid.uuid4())[:8]
        dept = {
            "id": dept_id,
            "org_id": org_id,
            "name": name,
            "description": description,
            "parent_id": parent_id,
            "members": [],
            "created_at": time.time(),
        }
        self._departments[dept_id] = dept
        return dept

    def get(self, dept_id: str) -> dict[str, Any] | None:
        return self._departments.get(dept_id)

    def list_by_org(self, org_id: str) -> list[dict[str, Any]]:
        return [d for d in self._departments.values() if d["org_id"] == org_id]

    def add_member(self, dept_id: str, user_id: str) -> bool:
        dept = self._departments.get(dept_id)
        if dept and user_id not in dept["members"]:
            dept["members"].append(user_id)
            return True
        return False

    def remove_member(self, dept_id: str, user_id: str) -> bool:
        dept = self._departments.get(dept_id)
        if dept and user_id in dept["members"]:
            dept["members"].remove(user_id)
            return True
        return False

    def delete(self, dept_id: str) -> bool:
        if dept_id in self._departments:
            del self._departments[dept_id]
            return True
        return False
