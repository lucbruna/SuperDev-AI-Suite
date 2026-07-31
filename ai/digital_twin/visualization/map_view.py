"""Map view."""
from __future__ import annotations

from typing import Any


class MapView:
    def __init__(self) -> None:
        self._markers: dict[str, dict[str, Any]] = {}
        self._layers: dict[str, list[str]] = {}
    def add_marker(self, marker_id: str, lat: float, lon: float, label: str = "", metadata: dict[str, Any] = None) -> dict[str, Any]:
        marker = {"marker_id": marker_id, "lat": lat, "lon": lon, "label": label, "metadata": metadata or {}}
        self._markers[marker_id] = marker
        return marker
    def get_marker(self, marker_id: str) -> dict[str, Any]:
        return self._markers.get(marker_id, {"error": "not_found"})
    def remove_marker(self, marker_id: str) -> bool:
        if marker_id in self._markers:
            del self._markers[marker_id]
            return True
        return False
    def create_layer(self, layer_name: str, marker_ids: list[str]) -> dict[str, Any]:
        self._layers[layer_name] = marker_ids
        return {"layer": layer_name, "markers": marker_ids}
    def get_layer(self, layer_name: str) -> list[dict[str, Any]]:
        marker_ids = self._layers.get(layer_name, [])
        return [self._markers[mid] for mid in marker_ids if mid in self._markers]
    def search(self, query: str) -> list[dict[str, Any]]:
        return [m for m in self._markers.values() if query.lower() in m.get("label", "").lower()]
    def list_markers(self) -> list[dict[str, Any]]:
        return list(self._markers.values())
    def count(self) -> int:
        return len(self._markers)
