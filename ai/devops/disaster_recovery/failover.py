"""Failover manager."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class FailoverManager:
    def __init__(self) -> None:
        self._configurations: Dict[str, Dict[str, Any]] = {}
        self._failovers: List[Dict[str, Any]] = []
    def configure(self, service: str, primary: str, secondary: str) -> Dict[str, Any]:
        config = {"service": service, "primary": primary, "secondary": secondary, "active": "primary"}
        self._configurations[service] = config
        return config
    def trigger_failover(self, service: str, reason: str = "") -> Dict[str, Any]:
        if service not in self._configurations:
            return {"error": "not_found"}
        config = self._configurations[service]
        config["active"] = "secondary"
        failover = {"service": service, "from": config["primary"], "to": config["secondary"], "reason": reason, "timestamp": time.time()}
        self._failovers.append(failover)
        return failover
    def failback(self, service: str) -> bool:
        if service in self._configurations:
            self._configurations[service]["active"] = "primary"
            return True
        return False
    def get_status(self, service: str) -> Dict[str, Any]:
        return self._configurations.get(service, {"error": "not_found"})
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._configurations.values())
    def get_failovers(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._failovers[-limit:]
    def count(self) -> int:
        return len(self._configurations)
