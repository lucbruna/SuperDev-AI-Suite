from __future__ import annotations

import time
from typing import Any


class ClusterSync:
    """Synchronizes memory across entire clusters."""

    def __init__(self):
        self._clusters: dict[str, dict[str, Any]] = {}
        self._cluster_log: list[dict[str, Any]] = []

    @property
    def cluster_count(self) -> int:
        return len(self._clusters)

    def register_cluster(self, cluster_id: str, node_ids: list[str] | None = None) -> None:
        self._clusters[cluster_id] = {
            "nodes": node_ids or [],
            "created_at": time.time(),
            "last_sync": 0.0,
        }

    def unregister_cluster(self, cluster_id: str) -> bool:
        return self._clusters.pop(cluster_id, None) is not None

    def add_node(self, cluster_id: str, node_id: str) -> bool:
        cluster = self._clusters.get(cluster_id)
        if cluster is None:
            return False
        if node_id not in cluster["nodes"]:
            cluster["nodes"].append(node_id)
        return True

    def remove_node(self, cluster_id: str, node_id: str) -> bool:
        cluster = self._clusters.get(cluster_id)
        if cluster is None or node_id not in cluster["nodes"]:
            return False
        cluster["nodes"].remove(node_id)
        return True

    def sync_cluster(self, cluster_id: str) -> dict[str, Any]:
        cluster = self._clusters.get(cluster_id)
        if cluster is None:
            return {"error": "cluster not found"}
        cluster["last_sync"] = time.time()
        entry = {"cluster_id": cluster_id, "timestamp": cluster["last_sync"], "node_count": len(cluster["nodes"])}
        self._cluster_log.append(entry)
        return entry

    def list_clusters(self) -> list[str]:
        return list(self._clusters.keys())

    def cluster_info(self, cluster_id: str) -> dict[str, Any] | None:
        return self._clusters.get(cluster_id)

    def clear(self) -> None:
        self._clusters.clear()
        self._cluster_log.clear()
