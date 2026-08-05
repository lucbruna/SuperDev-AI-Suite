"""Asset versions — versioning and rollback for assets."""
from __future__ import annotations

import time
from typing import Any


class AssetVersions:
    """Keeps a history of asset revisions."""

    def __init__(self) -> None:
        self._history: dict[str, list[dict[str, Any]]] = {}

    def commit(self, asset_id: str, *, ref: str, comment: str = "") -> int:
        version = len(self._history.get(asset_id, [])) + 1
        self._history.setdefault(asset_id, []).append(
            {"version": version, "ref": ref, "comment": comment, "created_at": time.time()}
        )
        return version

    def history(self, asset_id: str) -> list[dict[str, Any]]:
        return [dict(h) for h in self._history.get(asset_id, [])]

    def latest(self, asset_id: str) -> dict[str, Any] | None:
        history = self._history.get(asset_id)
        return dict(history[-1]) if history else None

    def rollback(self, asset_id: str, version: int) -> dict[str, Any] | None:
        history = self._history.get(asset_id, [])
        for entry in history:
            if entry["version"] == version:
                return dict(entry)
        return None
