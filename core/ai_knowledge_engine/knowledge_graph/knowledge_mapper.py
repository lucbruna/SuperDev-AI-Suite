from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from typing import Any


class KnowledgeMapper:
    def __init__(self) -> None:
        self._maps: dict[str, dict[str, Any]] = {}

    async def map_knowledge(self, map_id: str, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
        await asyncio.sleep(0.01)
        knowledge_map = {
            "id": map_id,
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
        }
        self._maps[map_id] = knowledge_map
        return knowledge_map

    async def create_map(self, map_id: str, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
        return await self.map_knowledge(map_id, nodes, edges)

    async def find_paths(self, adjacency: dict[str, list[str]], start: str, end: str) -> list[list[str]]:
        await asyncio.sleep(0.01)
        paths: list[list[str]] = []
        queue: deque[tuple[str, list[str]]] = deque()
        queue.append((start, [start]))

        while queue and len(paths) < 10:
            current, path = queue.popleft()
            for neighbor in adjacency.get(current, []):
                if neighbor not in path:
                    new_path = path + [neighbor]
                    if neighbor == end:
                        paths.append(new_path)
                    else:
                        queue.append((neighbor, new_path))
        return paths

    async def get_connected_components(self, adjacency: dict[str, list[str]]) -> list[list[str]]:
        await asyncio.sleep(0.01)
        visited: set[str] = set()
        components: list[list[str]] = []

        for node in adjacency:
            if node not in visited:
                component: list[str] = []
                queue: deque[str] = deque([node])
                while queue:
                    current = queue.popleft()
                    if current not in visited:
                        visited.add(current)
                        component.append(current)
                        for neighbor in adjacency.get(current, []):
                            if neighbor not in visited:
                                queue.append(neighbor)
                components.append(component)
        return components

    async def analyze_density(self, adjacency: dict[str, list[str]]) -> dict[str, Any]:
        await asyncio.sleep(0.01)
        n = len(adjacency)
        total_possible_edges = n * (n - 1) if n > 1 else 1
        actual_edges = sum(len(neighbors) for neighbors in adjacency.values())
        density = actual_edges / total_possible_edges if total_possible_edges > 0 else 0.0

        degrees = [len(neighbors) for neighbors in adjacency.values()]
        avg_degree = sum(degrees) / n if n > 0 else 0.0

        return {
            "node_count": n,
            "edge_count": actual_edges,
            "density": round(density, 4),
            "average_degree": round(avg_degree, 4),
            "is_dense": density > 0.5,
            "is_sparse": density < 0.1,
        }

    async def get_knowledge_map_summary(self, map_id: str) -> dict[str, Any]:
        await asyncio.sleep(0.01)
        knowledge_map = self._maps.get(map_id)
        if knowledge_map is None:
            return {"error": f"Map not found: {map_id}"}
        return {
            "id": knowledge_map["id"],
            "node_count": knowledge_map["node_count"],
            "edge_count": knowledge_map["edge_count"],
            "node_labels": list({n.get("label", "") for n in knowledge_map["nodes"]}),
            "edge_types": list({e.get("type", "") for e in knowledge_map["edges"]}),
        }