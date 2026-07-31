"""Security helpers for the automation engine."""

from __future__ import annotations

import re
from typing import Any

_SENSITIVE = {"password", "secret", "token", "api_key", "apikey", "authorization"}


class AutomationSecurity:
    """Sanitization and permission checks for automation payloads."""

    def __init__(self) -> None:
        self._allowed_actions: set[str] | None = None  # None = allow all

    def restrict_actions(self, allowed: list[str]) -> None:
        self._allowed_actions = set(allowed)

    def can_execute(self, action: str) -> bool:
        if self._allowed_actions is None:
            return True
        return action in self._allowed_actions

    @staticmethod
    def redact(data: dict[str, Any]) -> dict[str, Any]:
        """Returns a copy with sensitive values masked."""
        result: dict[str, Any] = {}
        for key, value in data.items():
            lowered = key.lower()
            if any(token in lowered for token in _SENSITIVE) and value is not None:
                result[key] = "***"
            elif isinstance(value, dict):
                result[key] = AutomationSecurity.redact(value)
            else:
                result[key] = value
        return result

    @staticmethod
    def sanitize_name(name: str) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9_\-]", "-", name.strip())
        return re.sub(r"-+", "-", cleaned)

    @staticmethod
    def validate_payload(payload: Any) -> list[str]:
        """Returns a list of validation issues (empty means valid)."""
        issues: list[str] = []
        if not isinstance(payload, dict):
            return ["payload must be a dict"]
        if len(str(payload)) > 1_000_000:
            issues.append("payload exceeds 1MB limit")
        return issues
