from __future__ import annotations

from typing import Any, Dict, Optional


class Approval:
    """Approval workflow for agent actions."""

    def __init__(self) -> None:
        self._requests: Dict[str, Dict[str, Any]] = {}

    def request(self, request_id: str, agent_id: str, action: str, reason: str) -> None:
        self._requests[request_id] = {"agent": agent_id, "action": action, "reason": reason, "status": "pending"}

    def approve(self, request_id: str) -> bool:
        req = self._requests.get(request_id)
        if req and req["status"] == "pending":
            req["status"] = "approved"
            return True
        return False

    def deny(self, request_id: str) -> bool:
        req = self._requests.get(request_id)
        if req and req["status"] == "pending":
            req["status"] = "denied"
            return True
        return False

    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        req = self._requests.get(request_id)
        return dict(req) if req else None

    def clear(self) -> None:
        self._requests.clear()
