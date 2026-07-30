from __future__ import annotations

from typing import Any, get_type_hints

from ..api_interfaces import IAPIValidator


class TypeValidator(IAPIValidator):
    """Validates data against Python type annotations."""

    async def validate(self, data: Any, schema: Any) -> dict[str, Any]:
        if not isinstance(data, dict):
            return {"valid": True, "data": data}

        errors: list[str] = []
        result: dict[str, Any] = {}

        for field_name, field_type in schema.items() if isinstance(schema, dict) else []:
            if field_name not in data:
                continue
            value = data[field_name]
            if field_type is str and not isinstance(value, str):
                errors.append(f"{field_name}: expected str, got {type(value).__name__}")
                result[field_name] = value
            elif field_type is int and not isinstance(value, int):
                if isinstance(value, float):
                    result[field_name] = int(value)
                else:
                    errors.append(f"{field_name}: expected int, got {type(value).__name__}")
                    result[field_name] = value
            elif field_type is float and not isinstance(value, (int, float)):
                errors.append(f"{field_name}: expected float, got {type(value).__name__}")
                result[field_name] = value
            elif field_type is bool and not isinstance(value, bool):
                errors.append(f"{field_name}: expected bool, got {type(value).__name__}")
                result[field_name] = value
            elif field_type is list and not isinstance(value, list):
                errors.append(f"{field_name}: expected list, got {type(value).__name__}")
                result[field_name] = value
            elif field_type is dict and not isinstance(value, dict):
                errors.append(f"{field_name}: expected dict, got {type(value).__name__}")
                result[field_name] = value
            else:
                result[field_name] = value

        if errors:
            return {"valid": False, "errors": errors, "data": result}
        return {"valid": True, "data": result}

    def to_dict(self) -> dict[str, Any]:
        return {"validator": "TypeValidator"}
