from __future__ import annotations

import re
from typing import Any

from ..api_interfaces import IAPIValidator
from ..api_models import APIError


class JSONSchemaValidator(IAPIValidator):
    """Validates data against a JSON-like schema (standard library only)."""

    def __init__(self) -> None:
        self._schemas: dict[str, dict[str, Any]] = {}

    def register_schema(self, name: str, schema: dict[str, Any]) -> None:
        self._schemas[name] = schema

    def get_schema(self, name: str) -> dict[str, Any] | None:
        return self._schemas.get(name)

    async def validate(self, data: Any, schema: Any) -> dict[str, Any]:
        if isinstance(schema, str):
            schema = self._schemas.get(schema, {})
        if not isinstance(schema, dict):
            return {"valid": True, "data": data}

        errors: list[str] = []
        schema_type = schema.get("type", "")

        if schema_type == "object" and isinstance(data, dict):
            props = schema.get("properties", {})
            required = set(schema.get("required", []))

            for req_field in required:
                if req_field not in data:
                    errors.append(f"Missing required field: {req_field}")

            for field_name, field_schema in props.items():
                if field_name in data:
                    field_result = await self.validate(data[field_name], field_schema)
                    if not field_result.get("valid"):
                        errors.append(f"{field_name}: {field_result.get('errors', ['Invalid'])}")

            additional = schema.get("additionalProperties", True)
            if not additional:
                allowed = set(props.keys())
                for key in data:
                    if key not in allowed:
                        errors.append(f"Unexpected field: {key}")

        elif schema_type == "array" and isinstance(data, (list, tuple)):
            items_schema = schema.get("items", {})
            min_items = schema.get("minItems", 0)
            max_items = schema.get("maxItems", float("inf"))

            if len(data) < min_items:
                errors.append(f"Array too short: min {min_items}")
            if len(data) > max_items:
                errors.append(f"Array too long: max {max_items}")

            for i, item in enumerate(data):
                item_result = await self.validate(item, items_schema)
                if not item_result.get("valid"):
                    errors.append(f"[{i}]: {item_result.get('errors', ['Invalid'])}")

        elif schema_type in ("string", "number", "integer", "boolean"):
            type_map = {
                "string": str,
                "number": (int, float),
                "integer": int,
                "boolean": bool,
            }
            expected_type = type_map.get(schema_type)
            if expected_type and not isinstance(data, expected_type):
                errors.append(f"Expected {schema_type}, got {type(data).__name__}")

            if schema_type == "string" and isinstance(data, str):
                pattern = schema.get("pattern", "")
                if pattern and not re.match(pattern, data):
                    errors.append(f"String does not match pattern: {pattern}")
                min_len = schema.get("minLength", 0)
                max_len = schema.get("maxLength", float("inf"))
                if len(data) < min_len:
                    errors.append(f"String too short: min {min_len}")
                if len(data) > max_len:
                    errors.append(f"String too long: max {max_len}")

            if schema_type in ("number", "integer") and isinstance(data, (int, float)):
                minimum = schema.get("minimum")
                maximum = schema.get("maximum")
                if minimum is not None and data < minimum:
                    errors.append(f"Value below minimum: {minimum}")
                if maximum is not None and data > maximum:
                    errors.append(f"Value above maximum: {maximum}")

        elif schema_type == "enum":
            allowed_values = schema.get("values", [])
            if data not in allowed_values:
                errors.append(f"Value not in enum: {data}")

        if errors:
            return {"valid": False, "errors": errors, "data": data}
        return {"valid": True, "data": data}

    def to_dict(self) -> dict[str, Any]:
        return {
            "validator": "JSONSchemaValidator",
            "schemas": list(self._schemas.keys()),
        }
