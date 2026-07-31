"""Uptime monitor."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class UptimeMonitor:
    def __init__(self) -> None:
        self._services: Dict[str, Dict[str, Any]] = {}
        self._checks: List[Dict[str, Any]] = []
    def register(self, name: str, url: str = "") -> Dict[str, Any]:
        service = {"name": name, "url": url, "status": "up", "uptime_pct": 99.9, "last_check": time.time()}
        self._services[name] = service
        return service
    def check(self, name: str) -> Dict[str, Any]:
        if name not in self._services:
            return {"error": "not_found"}
        self._services[name]["last_check"] = time.time()
        check = {"service": name, "status": "up", "latency_ms": 45.0, "timestamp": time.time()}
        self._checks.append(check)
        return check
    def get_status(self, name: str) -> Dict[str, Any]:
        return self._services.get(name, {"error": "not_found"})
    def list_services(self) -> List[Dict[str, Any]]:
        return list(self._services.values())
    def get_checks(self, name: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        checks = self._checks
        if name:
            checks = [c for c in checks if c.get("service") == name]
        return checks[-limit:]
    def count(self) -> int:
        return len(self._services)
