"""User invitations."""

from __future__ import annotations

import time
import uuid
from typing import Any


class InvitationManager:
    def __init__(self) -> None:
        self._invitations: dict[str, dict[str, Any]] = {}

    def create(self, email: str, org_id: str, role: str = "member", invited_by: str = "") -> dict[str, Any]:
        inv_id = str(uuid.uuid4())[:8]
        inv = {
            "id": inv_id,
            "email": email,
            "org_id": org_id,
            "role": role,
            "invited_by": invited_by,
            "status": "pending",
            "created_at": time.time(),
            "expires_at": time.time() + 7 * 86400,
        }
        self._invitations[inv_id] = inv
        return inv

    def get(self, inv_id: str) -> dict[str, Any] | None:
        return self._invitations.get(inv_id)

    def accept(self, inv_id: str) -> bool:
        inv = self._invitations.get(inv_id)
        if inv and inv["status"] == "pending":
            inv["status"] = "accepted"
            inv["accepted_at"] = time.time()
            return True
        return False

    def decline(self, inv_id: str) -> bool:
        inv = self._invitations.get(inv_id)
        if inv and inv["status"] == "pending":
            inv["status"] = "declined"
            return True
        return False

    def revoke(self, inv_id: str) -> bool:
        inv = self._invitations.get(inv_id)
        if inv:
            inv["status"] = "revoked"
            return True
        return False

    def list_pending(self, org_id: str = "") -> list[dict[str, Any]]:
        results = [i for i in self._invitations.values() if i["status"] == "pending"]
        if org_id:
            results = [i for i in results if i["org_id"] == org_id]
        return results

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._invitations.values())
