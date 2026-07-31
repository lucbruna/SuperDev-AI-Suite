"""Cleaning processors (trim, defaults, drop empty fields)."""

from __future__ import annotations

from typing import Any

from data_intelligence.processing.base import Processor


class TrimProcessor(Processor):
    """Strips whitespace from all string values."""

    name = "trim"

    def apply(self, record: dict[str, Any]) -> dict[str, Any]:
        return {k: v.strip() if isinstance(v, str) else v
                for k, v in record.items()}


class DefaultFiller(Processor):
    """Fills missing/empty fields with default values."""

    name = "defaults"

    def __init__(self, defaults: dict[str, Any]) -> None:
        self.defaults = defaults

    def apply(self, record: dict[str, Any]) -> dict[str, Any]:
        out = dict(record)
        for field, default in self.defaults.items():
            value = out.get(field)
            if value is None or value == "":
                out[field] = default
        return out


class DropEmptyProcessor(Processor):
    """Removes fields whose value is empty (None or "")."""

    name = "drop_empty"

    def apply(self, record: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in record.items()
                if v is not None and v != ""}
