"""Marker manager — named markers and comments on the timeline."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError


class MarkerManager:
    """Manages timeline markers (chapter points, notes, cue points)."""

    def __init__(self) -> None:
        self._markers: dict[str, dict[str, Any]] = {}

    def add(
        self,
        marker_id: str,
        position: float,
        label: str,
        color: str = "#3498db",
        **meta: Any,
    ) -> dict[str, Any]:
        if marker_id in self._markers:
            raise ValidationError(f"Marker '{marker_id}' already exists", field="marker_id")
        if position < 0:
            raise ValidationError("Marker position cannot be negative", field="position")
        marker = {"id": marker_id, "position": position, "label": label, "color": color, **meta}
        self._markers[marker_id] = marker
        return marker

    def get(self, marker_id: str) -> dict[str, Any] | None:
        return self._markers.get(marker_id)

    def update(self, marker_id: str, **changes: Any) -> dict[str, Any]:
        marker = self._require(marker_id)
        marker.update(changes)
        return marker

    def delete(self, marker_id: str) -> bool:
        return self._markers.pop(marker_id, None) is not None

    def list(self, start: float = 0.0, end: float | None = None) -> list[dict[str, Any]]:
        markers = sorted(self._markers.values(), key=lambda m: m["position"])
        return [m for m in markers if m["position"] >= start and (end is None or m["position"] <= end)]

    def markers_between(self, start: float, end: float) -> list[dict[str, Any]]:
        return self.list(start=start, end=end)

    def chapters(self) -> list[dict[str, Any]]:
        """Markers intended as chapter points (type == chapter or with chapters flag)."""
        return [m for m in self._markers.values() if m.get("type") == "chapter"]

    def count(self) -> int:
        return len(self._markers)

    def _require(self, marker_id: str) -> dict[str, Any]:
        marker = self._markers.get(marker_id)
        if marker is None:
            raise ValidationError(f"Marker '{marker_id}' not found", field="marker_id")
        return marker


_marker_manager: MarkerManager | None = None


def get_marker_manager() -> MarkerManager:
    global _marker_manager
    if _marker_manager is None:
        _marker_manager = MarkerManager()
    return _marker_manager
