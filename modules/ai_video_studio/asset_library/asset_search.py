"""Asset search — search assets by name, type and tags."""
from __future__ import annotations

from typing import Any


class AssetSearch:
    """Token-based search over asset metadata."""

    def search(self, assets: list[dict[str, Any]], *, query: str = "", asset_type: str | None = None) -> list[dict[str, Any]]:
        tokens = {w.lower() for w in query.split() if w}
        results = []
        for asset in assets:
            if asset_type is not None and asset["type"] != asset_type:
                continue
            if not tokens:
                results.append(asset)
                continue
            haystack = {asset["name"].lower()} | {t.lower() for t in asset.get("tags", [])} | {asset["type"].lower()}
            if tokens & haystack:
                results.append(asset)
        return results
