from __future__ import annotations

import logging
from typing import Any

from ..integration_models import ConnectionConfig


class ConnectorValidator:
    """Validates connector configurations against per-type schemas."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.connectors.validator")
        self._schemas: dict[str, dict[str, Any]] = {}

    def register_schema(self, connector_type: str, schema: dict[str, Any]) -> None:
        """Schema is a dict of field -> dict(required=bool, type=type name)."""
        self._schemas[connector_type] = schema

    def validate(self, config: ConnectionConfig) -> list[str]:
        """Returns a list of validation errors (empty when valid)."""
        schema = self._schemas.get(config.connector_type)
        if schema is None:
            return []
        errors: list[str] = []
        for field, rules in schema.items():
            if rules.get("required") and field not in config.config:
                errors.append(f"missing required field {field!r}")
            value = config.config.get(field)
            expected = rules.get("type")
            if value is not None and expected is not None:
                type_ok = {
                    "str": isinstance(value, str),
                    "int": isinstance(value, int) and not isinstance(value, bool),
                    "bool": isinstance(value, bool),
                    "list": isinstance(value, list),
                    "dict": isinstance(value, dict),
                }.get(expected, True)
                if not type_ok:
                    errors.append(f"field {field!r} must be {expected}")
        return errors

    def is_valid(self, config: ConnectionConfig) -> bool:
        return not self.validate(config)

    def snapshot(self) -> dict[str, int]:
        return {"schemas": len(self._schemas)}
