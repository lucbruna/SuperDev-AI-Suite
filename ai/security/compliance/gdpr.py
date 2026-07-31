"""GDPR compliance."""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any


class DataSubjectRights(Enum):
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    PORTABILITY = "portability"
    RESTRICTION = "restriction"
    OBJECTION = "objection"


class GDPRCompliance:
    def __init__(self) -> None:
        self._consent_records: dict[str, dict[str, Any]] = {}
        self._data_requests: list[dict[str, Any]] = []
        self._breach_log: list[dict[str, Any]] = []

    def record_consent(self, user_id: str, purpose: str, granted: bool) -> dict[str, Any]:
        record = {
            "user_id": user_id,
            "purpose": purpose,
            "granted": granted,
            "timestamp": time.time(),
            "consent_id": str(uuid.uuid4())[:8],
        }
        self._consent_records[record["consent_id"]] = record
        return record

    def has_consent(self, user_id: str, purpose: str) -> bool:
        for r in self._consent_records.values():
            if r["user_id"] == user_id and r["purpose"] == purpose and r["granted"]:
                return True
        return False

    def withdraw_consent(self, user_id: str, purpose: str) -> bool:
        for r in self._consent_records.values():
            if r["user_id"] == user_id and r["purpose"] == purpose:
                r["granted"] = False
                return True
        return False

    def submit_request(self, user_id: str, right: DataSubjectRights, details: str = "") -> dict[str, Any]:
        req = {
            "request_id": str(uuid.uuid4())[:8],
            "user_id": user_id,
            "right": right.value,
            "details": details,
            "timestamp": time.time(),
            "status": "pending",
        }
        self._data_requests.append(req)
        return req

    def process_request(self, request_id: str, status: str) -> bool:
        for req in self._data_requests:
            if req["request_id"] == request_id:
                req["status"] = status
                return True
        return False

    def report_breach(self, description: str, affected_users: int, severity: str = "medium") -> dict[str, Any]:
        breach = {
            "breach_id": str(uuid.uuid4())[:8],
            "description": description,
            "affected_users": affected_users,
            "severity": severity,
            "timestamp": time.time(),
            "reported_to_authority": False,
        }
        self._breach_log.append(breach)
        return breach

    def get_user_data(self, user_id: str) -> dict[str, Any]:
        consents = [r for r in self._consent_records.values() if r["user_id"] == user_id]
        requests = [r for r in self._data_requests if r["user_id"] == user_id]
        return {"user_id": user_id, "consents": consents, "requests": requests}

    def list_breaches(self) -> list[dict[str, Any]]:
        return list(self._breach_log)
