"""Server manager."""
from __future__ import annotations

import time
from typing import Any


class ServerManager:
    def __init__(self) -> None:
        self._servers: dict[str, dict[str, Any]] = {}
    def create(self, name: str, cpu: int = 4, memory_gb: int = 16, region: str = "us-east-1") -> dict[str, Any]:
        import uuid
        sid = str(uuid.uuid4())[:8]
        server = {"server_id": sid, "name": name, "cpu": cpu, "memory_gb": memory_gb, "region": region, "state": "running", "ip": f"10.0.{len(self._servers)+1}.1", "created_at": time.time()}
        self._servers[sid] = server
        return server
    def get(self, server_id: str) -> dict[str, Any]:
        return self._servers.get(server_id, {"error": "not_found"})
    def stop(self, server_id: str) -> bool:
        if server_id in self._servers:
            self._servers[server_id]["state"] = "stopped"
            return True
        return False
    def start(self, server_id: str) -> bool:
        if server_id in self._servers:
            self._servers[server_id]["state"] = "running"
            return True
        return False
    def terminate(self, server_id: str) -> bool:
        if server_id in self._servers:
            self._servers[server_id]["state"] = "terminated"
            return True
        return False
    def list_all(self) -> list[dict[str, Any]]:
        return list(self._servers.values())
    def list_by_region(self, region: str) -> list[dict[str, Any]]:
        return [s for s in self._servers.values() if s.get("region") == region]
    def count(self) -> int:
        return len(self._servers)
