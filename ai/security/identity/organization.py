"""Organization management."""
from __future__ import annotations

import time
import uuid
from typing import Any


class OrganizationManager:
    def __init__(self) -> None:
        self._orgs: dict[str, dict[str, Any]] = {}
    def create(self, name: str) -> dict[str, Any]:
        oid = str(uuid.uuid4())[:8]
        org = {"org_id": oid, "name": name, "created_at": time.time(), "members": []}
        self._orgs[oid] = org
        return {"org_id": oid, "name": name, "status": "created"}
    def get(self, org_id: str) -> dict[str, Any] | None:
        return dict(self._orgs[org_id]) if org_id in self._orgs else None
    def add_member(self, org_id: str, user_id: str) -> bool:
        if org_id in self._orgs:
            self._orgs[org_id]["members"].append(user_id)
            return True
        return False
    def count(self) -> int:
        return len(self._orgs)
