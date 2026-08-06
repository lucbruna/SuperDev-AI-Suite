"""Base helpers for configuration dataclasses."""
from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from typing import Any, get_args, get_origin

_TYPE_ALIASES: dict[type, tuple[type, ...]] = {}


def _coerce(field_type: Any, value: Any) -> Any:
    """Best-effort coercion of an override value to the dataclass field type."""
    origin = get_origin(field_type)
    args = get_args(field_type)
    if origin is None:
        # Plain type (int, str, bool, ...) — handle Optional via args below.
        if field_type is bool and isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        if value is None:
            return value
        try:
            return field_type(value)
        except (TypeError, ValueError):
            return value
    if origin is list and isinstance(value, (list, tuple)):
        inner = args[0] if args else Any
        return [_coerce(inner, item) for item in value]
    if origin is dict and isinstance(value, dict):
        key_t, val_t = args if len(args) == 2 else (Any, Any)
        return {k: _coerce(val_t, v) for k, v in value.items()}
    return value


def apply_overrides(instance: Any, overrides: dict[str, Any] | None) -> Any:
    """Return a new instance with the given overrides applied and coerced."""
    if not overrides:
        return instance
    current = asdict(instance)
    field_map = {f.name: f for f in fields(instance)}
    for key, value in overrides.items():
        if key in field_map and value is not None:
            current[key] = _coerce(field_map[key].type, value)
    return type(instance)(**current)


def is_config(obj: Any) -> bool:
    return is_dataclass(obj)
