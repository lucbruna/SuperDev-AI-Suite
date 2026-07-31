"""Validation for action definitions and parameters."""

from __future__ import annotations

from typing import Any

from automation.actions.action_models import ActionDefinition

_TYPE_CONVERTERS: dict[str, Any] = {
    "int": int,
    "float": float,
    "str": str,
    "bool": lambda v: v if isinstance(v, bool) else str(v).lower() in {"true", "1", "yes"},
    "list": lambda v: v if isinstance(v, list) else [v],
    "dict": lambda v: v if isinstance(v, dict) else {"value": v},
}


class ActionValidator:
    """Checks definitions and coerces parameters."""

    def validate_definition(self, definition: ActionDefinition) -> list[str]:
        issues: list[str] = []
        if not definition.action_id:
            issues.append("action_id is required")
        if not definition.name:
            issues.append("name is required")
        if definition.retries < 0:
            issues.append("retries cannot be negative")
        if definition.timeout is not None and definition.timeout <= 0:
            issues.append("timeout must be positive")
        return issues

    def validate_params(self, definition: ActionDefinition,
                        params: dict[str, Any]) -> list[str]:
        missing = [p for p in definition.required_params if p not in params]
        return [f"missing required param: {p}" for p in missing]

    def coerce_params(self, definition: ActionDefinition,
                      params: dict[str, Any]) -> dict[str, Any]:
        """Applies the declared schema types to known params."""
        if not definition.params_schema:
            return dict(params)
        result = dict(params)
        for field, type_name in definition.params_schema.items():
            if field in result:
                converter = _TYPE_CONVERTERS.get(type_name)
                if converter is not None:
                    try:
                        result[field] = converter(result[field])
                    except (TypeError, ValueError):
                        pass  # keep original value when coercion fails
        return result
