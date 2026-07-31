"""Node manager."""
from __future__ import annotations

from typing import Any


class NodeManager:
    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}
    def add_node(self, name: str, cluster: str, cpu: int = 4, memory_gb: int = 16) -> dict[str, Any]:
        node = {"name": name, "cluster": cluster, "cpu": cpu, "memory_gb": memory_gb, "status": "ready", "pods": 0}
        self._nodes[name] = node
        return node
    def get_node(self, name: str) -> dict[str, Any]:
        return self._nodes.get(name, {"error": "not_found"})
    def cordon(self, name: str) -> bool:
        if name in self._nodes:
            self._nodes[name]["status"] = "unschedulable"
            return True
        return False
    def uncordon(self, name: str) -> bool:
        if name in self._nodes:
            self._nodes[name]["status"] = "ready"
            return True
        return False
    def drain(self, name: str) -> dict[str, Any]:
        if name not in self._nodes:
            return {"error": "not_found"}
        self._nodes[name]["pods"] = 0
        self._nodes[name]["status"] = "drained"
        return {"node": name, "drained": True}
    def list_nodes(self) -> list[dict[str, Any]]:
        return list(self._nodes.values())
    def list_by_cluster(self, cluster: str) -> list[dict[str, Any]]:
        return [n for n in self._nodes.values() if n.get("cluster") == cluster]
    def count(self) -> int:
        return len(self._nodes)
