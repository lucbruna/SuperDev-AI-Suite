"""Digital Twin manager."""
from __future__ import annotations
from typing import Any, Dict, List, Optional

class TwinManager:
    def __init__(self) -> None:
        self._twins: Dict[str, Dict[str, Any]] = {}
    def create(self, twin_id: str, name: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        twin = {"twin_id": twin_id, "name": name, "config": config or {}, "entities": {}, "status": "created"}
        self._twins[twin_id] = twin
        return twin
    def get(self, twin_id: str) -> Optional[Dict[str, Any]]:
        return self._twins.get(twin_id)
    def update(self, twin_id: str, **kwargs: Any) -> bool:
        if twin_id not in self._twins:
            return False
        self._twins[twin_id].update(kwargs)
        return True
    def delete(self, twin_id: str) -> bool:
        if twin_id in self._twins:
            del self._twins[twin_id]
            return True
        return False
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._twins.values())
    def add_entity(self, twin_id: str, entity_id: str, entity_data: Dict[str, Any]) -> bool:
        if twin_id not in self._twins:
            return False
        self._twins[twin_id]["entities"][entity_id] = entity_data
        return True
    def get_entities(self, twin_id: str) -> Dict[str, Any]:
        return self._twins.get(twin_id, {}).get("entities", {})
    def count(self) -> int:
        return len(self._twins)
