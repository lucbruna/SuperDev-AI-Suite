"""License activation."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class LicenseActivation:
    def __init__(self) -> None:
        self._activations: Dict[str, List[Dict[str, Any]]] = {}
    def activate(self, license_id: str, machine_id: str = "", user_id: str = "") -> Dict[str, Any]:
        entry = {"license_id": license_id, "machine_id": machine_id, "user_id": user_id, "activated_at": time.time()}
        self._activations.setdefault(license_id, []).append(entry)
        return entry
    def deactivate(self, license_id: str, machine_id: str = "") -> bool:
        activations = self._activations.get(license_id, [])
        if machine_id:
            self._activations[license_id] = [a for a in activations if a.get("machine_id") != machine_id]
        else:
            self._activations.pop(license_id, None)
        return True
    def get_activations(self, license_id: str) -> List[Dict[str, Any]]:
        return list(self._activations.get(license_id, []))
    def activation_count(self, license_id: str) -> int:
        return len(self._activations.get(license_id, []))
    def is_active(self, license_id: str) -> bool:
        return self.activation_count(license_id) > 0
    def list_all(self) -> Dict[str, List[Dict[str, Any]]]:
        return dict(self._activations)
