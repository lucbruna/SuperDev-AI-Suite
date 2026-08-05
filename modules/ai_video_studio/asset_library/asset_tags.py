"""Asset tags — manage tagging and tag clouds for assets."""
from __future__ import annotations

from typing import Any


class AssetTags:
    """Tracks tag counts across assets."""

    def __init__(self) -> None:
        self._counts: dict[str, int] = {}

    def add(self, asset: dict[str, Any]) -> None:
        for tag in asset.get("tags", []):
            self._counts[tag] = self._counts.get(tag, 0) + 1

    def remove(self, asset: dict[str, Any]) -> None:
        for tag in asset.get("tags", []):
            if self._counts.get(tag, 0) > 0:
                self._counts[tag] -= 1

    def popular(self, limit: int = 10) -> list[tuple[str, int]]:
        return sorted(self._counts.items(), key=lambda item: item[1], reverse=True)[:limit]

    def all_tags(self) -> list[str]:
        return list(self._counts.keys())
