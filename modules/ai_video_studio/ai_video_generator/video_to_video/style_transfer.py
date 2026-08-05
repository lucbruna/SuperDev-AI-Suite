"""Style transfer — restyle a video to match a target aesthetic."""
from __future__ import annotations

from typing import Any


class StyleTransfer:
    """Applies a style model to each frame of a source video."""

    _STYLES = ("cinematic", "anime", "oil_paint", "watercolor", "noir", "vintage")

    def transfer(self, source: str, style: str = "cinematic") -> dict[str, Any]:
        if style not in self._STYLES:
            raise ValueError(f"Unknown style '{style}'")
        return {"source": source, "style": style, "transfer_model": f"style_{style}", "frames": 0}

    def available_styles(self) -> list[str]:
        return list(self._STYLES)
