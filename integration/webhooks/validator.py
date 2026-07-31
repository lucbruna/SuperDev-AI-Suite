"""Webhook payload validation."""

from __future__ import annotations

from typing import Any


class WebhookValidator:
    """Validates webhook payloads against expected event types and schema."""

    def __init__(self) -> None:
        self._schemas: dict[str, dict[str, str]] = {}

    def register_schema(self, event_type: str, schema: dict[str, str]) -> None:
        """Registers a field-name -> type mapping for an event type."""
        self._schemas[event_type] = schema

    def validate(self, event_type: str, payload: dict[str, Any]) -> list[str]:
        """Returns a list of validation errors (empty means valid)."""
        errors: list[str] = []
        schema = self._schemas.get(event_type)
        if schema is None:
            return errors
        for field, expected in schema.items():
            if field not in payload:
                errors.append(f"missing field {field!r}")
                continue
            actual = type(payload[field]).__name__
            if expected != "any" and actual != expected:
                errors.append(
                    f"field {field!r} expected {expected!r}, got {actual!r}"
                )
        return errors

    def is_valid(self, event_type: str, payload: dict[str, Any]) -> bool:
        return not self.validate(event_type, payload)
