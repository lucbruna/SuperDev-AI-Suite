"""Image parser — normalise image inputs into descriptors."""
from __future__ import annotations

from typing import Any


class ImageParser:
    """Reads image references and extracts basic metadata."""

    def parse(self, source: str) -> dict[str, Any]:
        ref = source.split(":", 1)[1] if source.startswith("image:") else source
        return {
            "ref": ref,
            "width": None,
            "height": None,
            "format": ref.rsplit(".", 1)[-1].lower() if "." in ref else "unknown",
        }

    def from_metadata(self, ref: str, width: int, height: int, fmt: str) -> dict[str, Any]:
        return {"ref": ref, "width": width, "height": height, "format": fmt}
