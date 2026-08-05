"""Asset index — build and query an index over assets."""
from __future__ import annotations

from typing import Any


class AssetIndex:
    """Maintains a name/type/tag index for fast lookups."""

    def __init__(self) -> None:
        self._by_type: dict[str, list[str]] = {}
        self._by_tag: dict[str, list[str]] = {}

    def index(self, asset: dict[str, Any]) -> None:
        self._by_type.setdefault(asset["type"], []).append(asset["id"])
        for tag in asset.get("tags", []):
            self._by_tag.setdefault(tag, []).append(asset["id"])

    def by_type(self, asset_type: str) -> list[str]:
        return list(self._by_type.get(asset_type, []))

    def by_tag(self, tag: str) -> list[str]:
        return list(self._by_tag.get(tag, []))

    def rebuild(self, assets: list[dict[str, Any]]) -> None:
        self._by_type.clear()
        self._by_tag.clear()
        for asset in assets:
            self.index(asset)
