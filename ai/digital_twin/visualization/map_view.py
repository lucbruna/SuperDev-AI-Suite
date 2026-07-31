"""Map view."""
from __future__ import annotations
from typing import Any, Dict, List

class MapView:
    def __init__(self) -> None:
        self._markers: Dict[str, Dict[str, Any]] = {}
        self._layers: Dict[str, List[str]] = {}
    def add_marker(self, marker_id: str, lat: float, lon: float, label: str = "", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        marker = {"marker_id": marker_id, "lat": lat, "lon": lon, "label": label, "metadata": metadata or {}}
        self._markers[marker_id] = marker
        return marker
    def get_marker(self, marker_id: str) -> Dict[str, Any]:
        return self._markers.get(marker_id, {"error": "not_found"})
    def remove_marker(self, marker_id: str) -> bool:
        if marker_id in self._markers:
            del self._markers[marker_id]
            return True
        return False
    def create_layer(self, layer_name: str, marker_ids: List[str]) -> Dict[str, Any]:
        self._layers[layer_name] = marker_ids
        return {"layer": layer_name, "markers": marker_ids}
    def get_layer(self, layer_name: str) -> List[Dict[str, Any]]:
        marker_ids = self._layers.get(layer_name, [])
        return [self._markers[mid] for mid in marker_ids if mid in self._markers]
    def search(self, query: str) -> List[Dict[str, Any]]:
        return [m for m in self._markers.values() if query.lower() in m.get("label", "").lower()]
    def list_markers(self) -> List[Dict[str, Any]]:
        return list(self._markers.values())
    def count(self) -> int:
        return len(self._markers)
