"""Protocol helpers shared by Data Intelligence subsystems."""

from __future__ import annotations

import uuid
from typing import Any, Protocol


class IngestionSink(Protocol):
    """Anything that can ingest records."""

    def ingest(self, records: list[dict[str, Any]]) -> dict[str, Any]: ...


class Trainable(Protocol):
    """Anything that can be trained."""

    def train(self, *args: Any, **kwargs: Any) -> Any: ...


def new_id(prefix: str) -> str:
    """Generates a prefixed unique identifier."""
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def safe_get(data: dict[str, Any], key: str, default: Any = None) -> Any:
    """Dot-path aware lookup: 'a.b.c' walks nested dicts."""
    value: Any = data
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    return value


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"true", "1", "yes", "sim", "on"}


def coerce_number(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).replace(",", ".").strip())


def numeric_values(records: list[dict[str, Any]],
                   field: str) -> list[float]:
    """Extracts numeric values for a field across records."""
    values: list[float] = []
    for record in records:
        value = safe_get(record, field)
        try:
            values.append(coerce_number(value))
        except (TypeError, ValueError):
            continue
    return values
