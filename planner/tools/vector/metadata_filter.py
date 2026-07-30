from __future__ import annotations

from typing import Any


class MetadataFilter:
    """Filter search results by metadata criteria."""

    @staticmethod
    def filter(results: list[dict[str, Any]], criteria: dict[str, Any]) -> list[dict[str, Any]]:
        filtered = results
        for key, value in criteria.items():
            filtered = [r for r in filtered if r.get("metadata", {}).get(key) == value]
        return filtered

    @staticmethod
    def range_filter(results: list[dict[str, Any]], key: str, min_val: float, max_val: float) -> list[dict[str, Any]]:
        return [
            r for r in results
            if min_val <= r.get("metadata", {}).get(key, 0) <= max_val
        ]
