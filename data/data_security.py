from __future__ import annotations

import hashlib
from typing import Any

from .data_models import DataClassification, DataRecord, RetentionPolicy


class DataSecurity:
    """Security manager for data operations — PII detection, masking, access, audit."""

    PII_KEYS = {
        "email", "cpf", "cnpj", "phone", "password", "token",
        "credit_card", "ssn", "address", "birth_date",
    }

    def __init__(self) -> None:
        self._access_roles: dict[str, set[str]] = {}
        self._audit_log: list[dict[str, Any]] = []

    # -- PII / masking -------------------------------------------------------

    def detect_pii(self, record: DataRecord) -> list[str]:
        """Return the keys in the record data that look like PII."""
        found: list[str] = []
        for key in record.data:
            if key.lower() in self.PII_KEYS:
                found.append(key)
        return found

    def mask_value(self, value: Any) -> str:
        text = str(value)
        if len(text) <= 4:
            return "*" * len(text)
        return text[:2] + "*" * (len(text) - 4) + text[-2:]

    def mask_pii(self, record: DataRecord) -> DataRecord:
        masked = DataRecord(
            id=record.id,
            source=record.source,
            timestamp=record.timestamp,
            data=dict(record.data),
            metadata=dict(record.metadata),
            state=record.state,
            quality=record.quality,
        )
        for key in self.detect_pii(record):
            masked.data[key] = self.mask_value(record.data[key])
        return masked

    @staticmethod
    def checksum(data: dict[str, Any]) -> str:
        payload = str(sorted(data.items())).encode()
        return hashlib.sha256(payload).hexdigest()

    # -- classification ------------------------------------------------------

    def classify(
        self,
        record: DataRecord,
        classification: DataClassification = DataClassification.INTERNAL,
    ) -> DataClassification:
        if self.detect_pii(record):
            return DataClassification.CONFIDENTIAL
        return classification

    # -- access control ------------------------------------------------------

    def grant(self, role: str, action: str) -> None:
        self._access_roles.setdefault(role, set()).add(action)

    def revoke(self, role: str, action: str) -> None:
        self._access_roles.get(role, set()).discard(action)

    def can(self, role: str, action: str) -> bool:
        return action in self._access_roles.get(role, set())

    # -- audit ---------------------------------------------------------------

    def audit(self, action: str, actor: str, details: dict[str, Any] | None = None) -> None:
        self._audit_log.append({
            "action": action,
            "actor": actor,
            "details": details or {},
        })

    def get_audit_log(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._audit_log[-limit:]

    # -- retention -----------------------------------------------------------

    @staticmethod
    def retention_days(policy: RetentionPolicy) -> int | None:
        if policy == RetentionPolicy.DELETE_AFTER_DAYS:
            return 90
        if policy == RetentionPolicy.ARCHIVE_AFTER_DAYS:
            return 365
        return None


__all__ = ["DataSecurity"]
