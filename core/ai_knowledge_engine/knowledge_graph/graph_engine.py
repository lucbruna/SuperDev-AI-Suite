from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .entity_manager import EntityManager
from .relationship_builder import RelationshipBuilder, RelationshipType
from .knowledge_mapper import KnowledgeMapper


class EngineState(Enum):
    IDLE = "idle"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class EngineConfig:
    max_nodes: int = 10000
    max_edges: int = 50000
    allow_duplicate_edges: bool = False
    auto_infer_relationships: bool = True


@dataclass
class EngineMetrics:
    total_nodes: int = 0
    total_edges: int = 0
    queries_executed: int = 0
    traversals_performed: int = 0
    subgraphs_extracted: int = 0
    average_query_time_ms: float = 0.0


@dataclass
class Node:
    id: str
    label: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    properties: dict[str, Any] = field(default_factory=dict)


class GraphEngine:
    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or EngineConfig()
        self.state = EngineState.IDLE
        self.metrics = EngineMetrics()
        self.entity_manager = EntityManager()
        self.relationship_builder = RelationshipBuilder()
        self.knowledge_mapper = KnowledgeMapper()
        self._nodes: dict[str, Node] = {}
        self._adjacency: dict[str, dict[str, list[Edge]]] = defaultdict(lambda: defaultdict(list))
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        self.state = EngineState.INITIALIZING
        await asyncio.sleep(0.01)
        self.state = EngineState.READY

    async def stop(self) -> None:
        self.state = EngineState.STOPPING
        await asyncio.sleep(0.01)
        self.state = EngineState.IDLE

    async def add_node(self, node_id: str, label: str, properties: dict[str, Any] | None = None) -> Node:
        if self.state != EngineState.READY:
            raise RuntimeError(f"Engine not ready, current state: {self.state.value}")

        async with self._lock:
            node = Node(id=node_id, label=label, properties=properties or {})
            self._nodes[node_id] = node
            await self.entity_manager.create_entity(node_id, label, properties or {})
            self.metrics.total_nodes = len(self._nodes)
            return node

    async def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        properties: dict[str, Any] | None = None,
    ) -> Edge:
        async with self._lock:
            if source_id not in self._nodes or target_id not in self._nodes:
                raise ValueError(f"Node not found: {source_id if source_id not in self._nodes else target_id}")

            if not self.config.allow_duplicate_edges:
                for existing in self._adjacency[source_id][target_id]:
                    if existing.relationship_type == relationship_type:
                        return existing

            edge = Edge(
                source_id=source_id,
                target_id=target_id,
                relationship_type=relationship_type,
                properties=properties or {},
            )
            self._adjacency[source_id][target_id].append(edge)
            await self.relationship_builder.create_relationship(
                source_id, target_id, relationship_type, properties or {}
            )
            self.metrics.total_edges = sum(
                len(edges) for target_map in self._adjacency.values() for edges in target_map.values()
            )
            return edge

    async def query(self, node_id: str, depth: int = 1) -> dict[str, Any]:
        start = asyncio.get_event_loop().time()
        if node_id not in self._nodes:
            raise ValueError(f"Node not found: {node_id}")

        result: dict[str, Any] = {
            "node": {"id": node_id, "label": self._nodes[node_id].label},
            "edges": [],
            "neighbors": [],
        }

        visited = {node_id}
        current_level = [node_id]

        for _ in range(depth):
            next_level: list[str] = []
            for current in current_level:
                for target_id, edges in self._adjacency.get(current, {}).items():
                    if target_id not in visited:
                        visited.add(target_id)
                        next_level.append(target_id)
                        for edge in edges:
                            result["edges"].append({
                                "source": edge.source_id,
                                "target": edge.target_id,
                                "type": edge.relationship_type.value,
                            })
                            if target_id in self._nodes:
                                result["neighbors"].append({
                                    "id": target_id,
                                    "label": self._nodes[target_id].label,
                                })
            current_level = next_level

        elapsed = (asyncio.get_event_loop().time() - start) * 1000
        self.metrics.queries_executed += 1
        self.metrics.average_query_time_ms = (
            self.metrics.average_query_time_ms
            + (elapsed - self.metrics.average_query_time_ms) / self.metrics.queries_executed
        )
        return result

    async def traverse(self, start_id: str, relationship_type: RelationshipType | None = None) -> list[dict[str, Any]]:
        if start_id not in self._nodes:
            raise ValueError(f"Node not found: {start_id}")

        visited: set[str] = set()
        path: list[dict[str, Any]] = []
        queue: list[str] = [start_id]

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            path.append({
                "id": current,
                "label": self._nodes[current].label,
            })

            for target_id, edges in self._adjacency.get(current, {}).items():
                if target_id not in visited:
                    if relationship_type is None:
                        queue.append(target_id)
                    else:
                        for edge in edges:
                            if edge.relationship_type == relationship_type:
                                queue.append(target_id)
                                break

        self.metrics.traversals_performed += 1
        return path

    async def get_subgraph(self, node_ids: list[str]) -> dict[str, Any]:
        subgraph_nodes: dict[str, Node] = {}
        subgraph_edges: list[Edge] = []

        for nid in node_ids:
            if nid in self._nodes:
                subgraph_nodes[nid] = self._nodes[nid]

        node_set = set(subgraph_nodes.keys())
        for source_id, target_map in self._adjacency.items():
            if source_id in node_set:
                for target_id, edges in target_map.items():
                    if target_id in node_set:
                        subgraph_edges.extend(edges)

        self.metrics.subgraphs_extracted += 1
        return {
            "nodes": [{"id": n.id, "label": n.label} for n in subgraph_nodes.values()],
            "edges": [
                {"source": e.source_id, "target": e.target_id, "type": e.relationship_type.value}
                for e in subgraph_edges
            ],
        }