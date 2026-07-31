"""Data mapper."""
from __future__ import annotations
from typing import Any, Dict, List

class DataMapper:
    def __init__(self) -> None:
        self._mappings: Dict[str, Dict[str, Any]] = {}
    def add_mapping(self, name: str, source_field: str, target_field: str, transform: str = "") -> Dict[str, Any]:
        mapping = {"name": name, "source": source_field, "target": target_field, "transform": transform}
        self._mappings[name] = mapping
        return mapping
    def map_data(self, mapping_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        mapping = self._mappings.get(mapping_name, {})
        source = mapping.get("source", "")
        target = mapping.get("target", "")
        value = data.get(source)
        if value is None:
            return {"error": "field_not_found"}
        transform = mapping.get("transform", "")
        if transform == "upper" and isinstance(value, str):
            value = value.upper()
        elif transform == "lower" and isinstance(value, str):
            value = value.lower()
        return {target: value}
    def map_batch(self, mapping_name: str, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.map_data(mapping_name, r) for r in records]
    def list_mappings(self) -> List[Dict[str, Any]]:
        return list(self._mappings.values())
    def get_mapping(self, name: str) -> Dict[str, Any]:
        return self._mappings.get(name, {"error": "not_found"})
    def delete_mapping(self, name: str) -> bool:
        if name in self._mappings:
            del self._mappings[name]
            return True
        return False
    def count(self) -> int:
        return len(self._mappings)
