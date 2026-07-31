"""Security helpers for the Data Intelligence Engine."""

from __future__ import annotations

from typing import Any

from data_intelligence.data_models import DataClassification


class DataIntelligenceSecurity:
    """Sanitization, masking and access control for data operations."""

    def __init__(self) -> None:
        self._permissions: dict[str, set[str]] = {}
        self._audit: list[dict[str, Any]] = []

    def grant(self, role: str, dataset: str) -> None:
        self._permissions.setdefault(role, set()).add(dataset)

    def can_access(self, role: str, dataset: str) -> bool:
        return dataset in self._permissions.get(role, set())

    def mask_pii(self, value: Any, kind: str = "default") -> Any:
        """Masks common PII shapes (email, cpf, phone, name)."""
        if not isinstance(value, str) or not value:
            return value
        if kind == "email" or "@" in value and "." in value:
            local, _, domain = value.partition("@")
            return f"{local[0]}***@{domain}" if local else value
        if kind == "cpf" or len(value) == 11 and value.isdigit():
            return f"{value[:3]}.***.***-{value[-2:]}"
        if kind == "phone" or len(value) >= 10 and any(c.isdigit() for c in value):
            return f"+{value[0]}****{value[-2:]}"
        if kind == "name":
            parts = value.split()
            if not parts:
                return value
            return f"{parts[0]} {''.join(p[0] + '.' for p in parts[1:])}"
        return value[:2] + "*" * max(0, len(value) - 4) + value[-2:]

    def classify(self, dataset: str) -> DataClassification:
        """Classifies a dataset by its name (heuristic)."""
        name = dataset.lower()
        if any(key in name for key in ("pii", "cpf", "email", "finance",
                                       "salary", "salary", "health")):
            return DataClassification.CONFIDENTIAL
        if any(key in name for key in ("internal", "employee", "sales",
                                       "inventory", "customer")):
            return DataClassification.INTERNAL
        return DataClassification.PUBLIC

    def audit(self, role: str, action: str, dataset: str) -> None:
        self._audit.append({"role": role, "action": action,
                            "dataset": dataset})

    def audit_log(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._audit[-limit:])
