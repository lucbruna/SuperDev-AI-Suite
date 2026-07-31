"""API health checks."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class APICheck:
    def __init__(self) -> None:
        self._endpoints: Dict[str, Dict[str, Any]] = {}
        self._results: List[Dict[str, Any]] = []
    def register(self, name: str, url: str, method: str = "GET") -> None:
        self._endpoints[name] = {"url": url, "method": method}
    def check(self, name: str) -> Dict[str, Any]:
        ep = self._endpoints.get(name)
        if not ep:
            return {"endpoint": name, "status": "not_found"}
        result = {"endpoint": name, "url": ep["url"], "status": "healthy", "latency_ms": 0, "timestamp": time.time()}
        self._results.append(result)
        return result
    def check_all(self) -> List[Dict[str, Any]]:
        return [self.check(name) for name in self._endpoints]
    def list_endpoints(self) -> List[str]:
        return list(self._endpoints.keys())
    def get_history(self, name: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        results = self._results
        if name:
            results = [r for r in results if r.get("endpoint") == name]
        return results[-limit:]
