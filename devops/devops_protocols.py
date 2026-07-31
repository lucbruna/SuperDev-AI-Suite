from __future__ import annotations

from typing import Any, TypeVar

T = TypeVar("T")


class DevOpsProtocols:
    """Collection of DevOps type protocols and helpers."""

    @staticmethod
    def validate_config(config: dict[str, Any], required: list[str]) -> list[str]:
        missing = [k for k in required if k not in config]
        return missing

    @staticmethod
    def merge_config(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        result = dict(base)
        result.update(override)
        return result
