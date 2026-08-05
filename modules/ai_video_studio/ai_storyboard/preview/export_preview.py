"""Export preview — describes the export-ready storyboard."""
from __future__ import annotations

from typing import Any


class ExportPreview:
    """Produces an export-ready preview descriptor."""

    def render(self, storyboard: dict[str, Any]) -> dict[str, Any]:
        boards = storyboard.get("boards", [])
        return {
            "name": storyboard.get("name", "storyboard"),
            "frame_count": len(boards),
            "total_duration": sum(b.get("duration", 2.5) for b in boards),
            "layout": storyboard.get("layout", {}).get("name", "cinematic"),
            "export_ready": True,
        }


_export_preview: ExportPreview | None = None


def get_export_preview() -> ExportPreview:
    global _export_preview
    if _export_preview is None:
        _export_preview = ExportPreview()
    return _export_preview
