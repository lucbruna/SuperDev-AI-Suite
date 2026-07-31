from __future__ import annotations

import logging
from typing import Any

from ..integration_models import APIEndpoint


class SchemaManager:
    """Validates request/response payloads against declared schemas."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.api.schemas")
        self._schemas: dict[str, dict[str, Any]] = {}

    def register(self, name: str, schema: dict[str, Any]) -> None:
        self._schemas[name] = schema

    def get(self, name: str) -> dict[str, Any] | None:
        return self._schemas.get(name)

    def list(self) -> list[str]:
        return sorted(self._schemas)

    def validate(self, name: str, payload: Any) -> bool:
        """Validates a payload against a JSON-schema-style map.

        Supported keywords: type (object/list/str/int/float/bool), properties,
        required, items, enum.
        """
        schema = self._schemas.get(name)
        if schema is None:
            raise KeyError(f"unknown schema {name!r}")
        return self._check(schema, payload)

    def _check(self, schema: dict[str, Any], value: Any) -> bool:
        expected = schema.get("type")
        if expected is not None:
            type_ok = {
                "object": isinstance(value, dict),
                "list": isinstance(value, list),
                "str": isinstance(value, str),
                "int": isinstance(value, int) and not isinstance(value, bool),
                "float": isinstance(value, (int, float)) and not isinstance(value, bool),
                "bool": isinstance(value, bool),
            }.get(expected, False)
            if not type_ok:
                return False
        if expected == "object" and isinstance(value, dict):
            required = schema.get("required", [])
            for field in required:
                if field not in value:
                    return False
            properties = schema.get("properties", {})
            for field, prop_schema in properties.items():
                if field in value and not self._check(prop_schema, value[field]):
                    return False
        if expected == "list" and isinstance(value, list):
            items_schema = schema.get("items")
            if items_schema is not None:
                for item in value:
                    if not self._check(items_schema, item):
                        return False
        enum = schema.get("enum")
        if enum is not None and value not in enum:
            return False
        return True

    def snapshot(self) -> dict[str, int]:
        return {"schemas": len(self._schemas)}
