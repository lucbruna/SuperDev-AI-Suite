"""Subscription activation."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class ActivationManager:
    def __init__(self) -> None:
        self._activations: Dict[str, Dict[str, Any]] = {}
    def activate(self, subscription_id: str, org_id: str) -> Dict[str, Any]:
        activation = {"subscription_id": subscription_id, "org_id": org_id, "status": "active", "activated_at": time.time()}
        self._activations[subscription_id] = activation
        return activation
    def deactivate(self, subscription_id: str) -> bool:
        if subscription_id in self._activations:
            self._activations[subscription_id]["status"] = "inactive"
            self._activations[subscription_id]["deactivated_at"] = time.time()
            return True
        return False
    def get(self, subscription_id: str) -> Dict[str, Any]:
        return self._activations.get(subscription_id, {})
    def list_by_org(self, org_id: str) -> List[Dict[str, Any]]:
        return [a for a in self._activations.values() if a["org_id"] == org_id]
    def is_active(self, subscription_id: str) -> bool:
        return self._activations.get(subscription_id, {}).get("status") == "active"
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._activations.values())
