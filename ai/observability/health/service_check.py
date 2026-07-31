"""Service health checks."""
from __future__ import annotations
from typing import Any, Callable, Dict, List
import time

class ServiceCheck:
    def __init__(self) -> None:
        self._services: Dict[str, Callable[[], bool]] = {}
        self._results: Dict[str, Dict[str, Any]] = {}
    def register(self, name: str, check_func: Callable[[], bool]) -> None:
        self._services[name] = check_func
    def check(self, name: str) -> Dict[str, Any]:
        func = self._services.get(name)
        if not func:
            return {"service": name, "status": "unknown", "message": "not_registered"}
        try:
            start = time.time()
            healthy = func()
            elapsed = (time.time() - start) * 1000
            result = {"service": name, "status": "healthy" if healthy else "unhealthy", "latency_ms": elapsed}
        except Exception as e:
            result = {"service": name, "status": "error", "error": str(e)}
        self._results[name] = result
        return result
    def check_all(self) -> Dict[str, Dict[str, Any]]:
        for name in self._services:
            self.check(name)
        return dict(self._results)
    def list_services(self) -> List[str]:
        return list(self._services.keys())
    def get_result(self, name: str) -> Dict[str, Any]:
        return self._results.get(name, {})
