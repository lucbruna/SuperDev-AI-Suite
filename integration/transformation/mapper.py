"""Field mapping between source and target structures."""

from __future__ import annotations

from typing import Any


class FieldMapper:
    """Maps source fields to target fields with optional default values."""

    def __init__(self) -> None:
        self._mappings: dict[str, str] = {}
        self._defaults: dict[str, Any] = {}

    def map(self, source_field: str, target_field: str,
            default: Any = None) -> None:
        self._mappings[target_field] = source_field
        self._defaults[target_field] = default

    def apply(self, source: dict[str, Any]) -> dict[str, Any]:
        target: dict[str, Any] = {}
        for target_field, source_field in self._mappings.items():
            if source_field in source and source[source_field] is not None:
                target[target_field] = source[source_field]
            elif self._defaults[target_field] is not None:
                target[target_field] = self._defaults[target_field]
        return target

    def fields(self) -> list[str]:
        return list(self._mappings)
