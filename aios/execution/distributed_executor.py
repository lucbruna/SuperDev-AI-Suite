"""DistributedExecutor: node registry, health and deterministic job assignment."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class WorkerNode:
    node_id: str
    capacity: int = 1
    healthy: bool = True
    busy: int = 0
    assigned: list[str] = field(default_factory=list)


class DistributedExecutor:
    """In-memory worker pool with round-robin assignment over healthy nodes."""

    def __init__(self) -> None:
        self._nodes: dict[str, WorkerNode] = {}
        self._rr = 0

    def register_node(self, node_id: str, capacity: int = 1) -> WorkerNode:
        if node_id in self._nodes:
            raise KeyError(f"node {node_id!r} already registered")
        node = WorkerNode(node_id=node_id, capacity=max(1, int(capacity)))
        self._nodes[node_id] = node
        return node

    def unregister_node(self, node_id: str) -> bool:
        return self._nodes.pop(node_id, None) is not None

    def node(self, node_id: str) -> WorkerNode | None:
        return self._nodes.get(node_id)

    def nodes(self) -> list[WorkerNode]:
        return [self._nodes[node_id] for node_id in sorted(self._nodes)]

    def set_health(self, node_id: str, healthy: bool) -> bool:
        node = self._nodes.get(node_id)
        if node is None:
            return False
        node.healthy = bool(healthy)
        return True

    def healthy_nodes(self) -> list[str]:
        return [
            node_id for node_id in sorted(self._nodes)
            if self._nodes[node_id].healthy
        ]

    def assign(self, job_id: str, node_id: str | None = None) -> str | None:
        """Assign a job to a healthy node with spare capacity; round-robin by default."""
        candidates = [
            name for name in sorted(self._nodes)
            if self._nodes[name].healthy and self._nodes[name].busy < self._nodes[name].capacity
        ]
        if not candidates:
            return None
        if node_id is not None:
            if node_id not in candidates:
                return None
            target = node_id
        else:
            target = candidates[self._rr % len(candidates)]
            self._rr += 1
        node = self._nodes[target]
        node.busy += 1
        node.assigned.append(job_id)
        return target

    def release(self, node_id: str, job_id: str) -> bool:
        node = self._nodes.get(node_id)
        if node is None:
            return False
        if job_id in node.assigned:
            node.assigned.remove(job_id)
        node.busy = max(0, node.busy - 1)
        return True

    def run_on(self, node_id: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        node = self._nodes.get(node_id)
        if node is None:
            raise KeyError(f"unknown node {node_id!r}")
        if not node.healthy:
            raise RuntimeError(f"node {node_id!r} is unhealthy")
        return fn(*args, **kwargs)

    def stats(self) -> dict[str, Any]:
        return {
            "total": len(self._nodes),
            "healthy": sum(1 for n in self._nodes.values() if n.healthy),
            "busy": sum(n.busy for n in self._nodes.values()),
            "capacity": sum(n.capacity for n in self._nodes.values()),
        }
