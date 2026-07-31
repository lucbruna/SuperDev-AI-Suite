"""License engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class LicenseEngine:
    def __init__(self) -> None:
        self._licenses: Dict[str, Dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def create(self, org_id: str, plan_id: str, key: str, max_activations: int = 1) -> Dict[str, Any]:
        import uuid
        lic_id = str(uuid.uuid4())[:8]
        lic = {"id": lic_id, "org_id": org_id, "plan_id": plan_id, "key": key, "status": "active", "max_activations": max_activations, "activations": 0, "created_at": time.time()}
        self._licenses[lic_id] = lic
        return lic
    def get(self, lic_id: str) -> Optional[Dict[str, Any]]:
        return self._licenses.get(lic_id)
    def get_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        for lic in self._licenses.values():
            if lic["key"] == key:
                return lic
        return None
    def revoke(self, lic_id: str) -> bool:
        lic = self._licenses.get(lic_id)
        if lic:
            lic["status"] = "revoked"
            return True
        return False
    def list_by_org(self, org_id: str) -> List[Dict[str, Any]]:
        return [l for l in self._licenses.values() if l["org_id"] == org_id]
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._licenses.values())
    def count(self) -> int:
        return len(self._licenses)
    def is_running(self) -> bool:
        return self._started
