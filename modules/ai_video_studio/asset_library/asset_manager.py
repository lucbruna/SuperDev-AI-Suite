"""Asset manager — central registry for reusable creative assets."""
from __future__ import annotations

import time
from typing import Any

from modules.ai_video_studio.core.exceptions import AssetNotFoundError


class AssetManager:
    """Stores assets with metadata and version tracking."""

    def __init__(self) -> None:
        self._assets: dict[str, dict[str, Any]] = {}

    def add(
        self,
        *,
        asset_type: str,
        name: str,
        ref: str,
        tags: list[str] | None = None,
        asset_id: str | None = None,
    ) -> str:
        aid = asset_id or f"asset_{len(self._assets) + 1}"
        self._assets[aid] = {
            "id": aid,
            "type": asset_type,
            "name": name,
            "ref": ref,
            "tags": tags or [],
            "created_at": time.time(),
            "version": 1,
        }
        return aid

    def get(self, asset_id: str) -> dict[str, Any]:
        asset = self._assets.get(asset_id)
        if asset is None:
            raise AssetNotFoundError(asset_id)
        return dict(asset)

    def delete(self, asset_id: str) -> bool:
        return self._assets.pop(asset_id, None) is not None

    def list(self, *, asset_type: str | None = None) -> list[dict[str, Any]]:
        assets = list(self._assets.values())
        if asset_type is not None:
            assets = [a for a in assets if a["type"] == asset_type]
        return [dict(a) for a in assets]

    def count(self) -> int:
        return len(self._assets)

    def generate_placeholder(self, *, name: str, kind: str = "texture") -> dict[str, Any]:
        """Generate a real placeholder asset (PNG texture or WAV sound).

        The generated file is registered in the manager and returned with
        its real output path.
        """
        from modules.ai_video_studio.asset_library.generate import generate_sound, generate_texture

        if kind in ("sound", "music"):
            result = generate_sound(name, kind="chord" if kind == "music" else "tone")
            self.add(asset_type=kind, name=name, ref=result["output_path"], tags=["generated"])
            return result
        result = generate_texture(name)
        self.add(asset_type=kind, name=name, ref=result["output_path"], tags=["generated"])
        return result
