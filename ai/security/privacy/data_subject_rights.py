"""Data subject rights."""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any


class RightType(Enum):
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    PORTABILITY = "portability"
    RESTRICTION = "restriction"
    OBJECTION = "objection"
    WITHDRAW_CONSENT = "withdraw_consent"


class DataSubjectRequest:
    def __init__(self, user_id: str, right: RightType, details: str = "") -> None:
        self.request_id = str(uuid.uuid4())[:8]
        self.user_id = user_id
        self.right = right
        self.details = details
        self.status = "pending"
        self.created_at = time.time()
        self.completed_at: float | None = None


class DataSubjectRightsManager:
    def __init__(self) -> None:
        self._requests: dict[str, DataSubjectRequest] = {}
        self._processing_log: list[dict[str, Any]] = []

    def submit_request(self, user_id: str, right: RightType, details: str = "") -> DataSubjectRequest:
        request = DataSubjectRequest(user_id, right, details)
        self._requests[request.request_id] = request
        return request

    def process_request(self, request_id: str, status: str = "completed", response: str = "") -> dict[str, Any]:
        request = self._requests.get(request_id)
        if not request:
            return {"error": "request_not_found"}
        request.status = status
        request.completed_at = time.time()
        entry = {
            "request_id": request_id,
            "user_id": request.user_id,
            "right": request.right.value,
            "status": status,
            "response": response,
            "timestamp": time.time(),
        }
        self._processing_log.append(entry)
        return entry

    def get_request(self, request_id: str) -> dict[str, Any] | None:
        request = self._requests.get(request_id)
        if request:
            return {
                "id": request.request_id,
                "user_id": request.user_id,
                "right": request.right.value,
                "status": request.status,
                "details": request.details,
                "created_at": request.created_at,
            }
        return None

    def get_user_requests(self, user_id: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for r in self._requests.values():
            if r.user_id == user_id:
                request = self.get_request(r.request_id)
                if request:
                    results.append(request)
        return results

    def list_pending(self) -> list[str]:
        return [r.request_id for r in self._requests.values() if r.status == "pending"]

    def get_processing_log(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._processing_log[-limit:]

    def stats(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for r in self._requests.values():
            counts[r.status] = counts.get(r.status, 0) + 1
        return counts
