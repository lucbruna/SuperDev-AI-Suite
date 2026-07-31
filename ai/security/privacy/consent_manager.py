"""Consent management."""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any


class ConsentType(Enum):
    IMPLICIT = "implicit"
    EXPLICIT = "explicit"
    OPT_IN = "opt_in"
    OPT_OUT = "opt_out"


class ConsentRecord:
    def __init__(self, user_id: str, purpose: str, consent_type: ConsentType, granted: bool) -> None:
        self.consent_id = str(uuid.uuid4())[:8]
        self.user_id = user_id
        self.purpose = purpose
        self.consent_type = consent_type
        self.granted = granted
        self.timestamp = time.time()
        self.expires_at = time.time() + (365 * 86400)


class ConsentManager:
    def __init__(self) -> None:
        self._records: dict[str, ConsentRecord] = {}
        self._purposes: dict[str, dict[str, Any]] = {}

    def register_purpose(self, purpose: str, description: str = "", required: bool = False) -> None:
        self._purposes[purpose] = {"description": description, "required": required}

    def record_consent(self, user_id: str, purpose: str, consent_type: ConsentType, granted: bool) -> ConsentRecord:
        record = ConsentRecord(user_id, purpose, consent_type, granted)
        self._records[record.consent_id] = record
        return record

    def has_consent(self, user_id: str, purpose: str) -> bool:
        for r in self._records.values():
            if r.user_id == user_id and r.purpose == purpose and r.granted and r.expires_at > time.time():
                return True
        return False

    def withdraw_consent(self, user_id: str, purpose: str) -> bool:
        for r in self._records.values():
            if r.user_id == user_id and r.purpose == purpose and r.granted:
                r.granted = False
                return True
        return False

    def get_user_consents(self, user_id: str) -> list[dict[str, Any]]:
        return [
            {
                "consent_id": r.consent_id,
                "purpose": r.purpose,
                "type": r.consent_type.value,
                "granted": r.granted,
                "timestamp": r.timestamp,
            }
            for r in self._records.values()
            if r.user_id == user_id
        ]

    def list_purposes(self) -> list[str]:
        return list(self._purposes.keys())

    def get_purpose_info(self, purpose: str) -> dict[str, Any] | None:
        return self._purposes.get(purpose)

    def cleanup_expired(self) -> int:
        now = time.time()
        expired = [k for k, v in self._records.items() if v.expires_at < now]
        for k in expired:
            del self._records[k]
        return len(expired)
