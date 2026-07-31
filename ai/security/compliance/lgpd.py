"""LGPD compliance (Lei Geral de Proteção de Dados)."""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any


class LGPDBasis(Enum):
    CONSENT = "consent"
    LEGITIMATE_INTEREST = "legitimate_interest"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    PUBLIC_INTEREST = "public_interest"
    HEALTH_PROTECTION = "health_protection"


class LGPDCompliance:
    def __init__(self) -> None:
        self._consent_records: dict[str, dict[str, Any]] = {}
        self._data_processing: list[dict[str, Any]] = []
        self._dpo_activities: list[dict[str, Any]] = []

    def record_consent(self, user_id: str, purpose: str, granted: bool) -> dict[str, Any]:
        record = {
            "consent_id": str(uuid.uuid4())[:8],
            "user_id": user_id,
            "purpose": purpose,
            "granted": granted,
            "timestamp": time.time(),
        }
        self._consent_records[record["consent_id"]] = record
        return record

    def has_consent(self, user_id: str, purpose: str) -> bool:
        for r in self._consent_records.values():
            if r["user_id"] == user_id and r["purpose"] == purpose and r["granted"]:
                return True
        return False

    def register_processing(self, purpose: str, basis: LGPDBasis, data_categories: list[str]) -> dict[str, Any]:
        proc = {
            "processing_id": str(uuid.uuid4())[:8],
            "purpose": purpose,
            "basis": basis.value,
            "categories": data_categories,
            "timestamp": time.time(),
        }
        self._data_processing.append(proc)
        return proc

    def dpo_activity(self, activity_type: str, details: str, dpo: str = "") -> dict[str, Any]:
        entry = {
            "activity_id": str(uuid.uuid4())[:8],
            "type": activity_type,
            "details": details,
            "dpo": dpo,
            "timestamp": time.time(),
        }
        self._dpo_activities.append(entry)
        return entry

    def get_user_consent(self, user_id: str) -> list[dict[str, Any]]:
        return [r for r in self._consent_records.values() if r["user_id"] == user_id]

    def list_processing_activities(self) -> list[dict[str, Any]]:
        return list(self._data_processing)

    def list_dpo_activities(self) -> list[dict[str, Any]]:
        return list(self._dpo_activities)
