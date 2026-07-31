from __future__ import annotations

import time
from typing import Any


class DistributedMemory:
    """Manages distributed memory across multiple nodes."""

    def __init__(self):
        self._nodes: dict[str, dict[str, Any]] = {}
        self._partitions: dict[str, list[str]] = {}

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    def register_node(self, node_id: str, metadata: dict[str, Any] | None = None) -> None:
        self._nodes[node_id] = {"metadata": metadata or {}, "registered_at": time.time()}

    def unregister_node(self, node_id: str) -> bool:
        return self._nodes.pop(node_id, None) is not None

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        return self._nodes.get(node_id)

    def list_nodes(self) -> list[str]:
        return list(self._nodes.keys())

    def assign_partition(self, partition_id: str, node_ids: list[str]) -> None:
        self._partitions[partition_id] = list(node_ids)

    def get_partition(self, partition_id: str) -> list[str] | None:
        return self._partitions.get(partition_id)

    def get_node_partitions(self, node_id: str) -> list[str]:
        return [p for p, nodes in self._partitions.items() if node_id in nodes]

    def distribute(self, data: dict[str, Any]) -> dict[str, list[str]]:
        mapping: dict[str, list[str]] = {}
        if not self._nodes:
            return mapping
        node_ids = list(self._nodes.keys())
        for i, (key, _value) in enumerate(data.items()):
            node = node_ids[i % len(node_ids)]
            mapping.setdefault(node, []).append(key)
        return mapping

    def clear(self) -> None:
        self._nodes.clear()
        self._partitions.clear()
