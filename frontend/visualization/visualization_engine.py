from __future__ import annotations

import logging
from typing import Any


class VisualizationEngine:
    """Coordinates graph and chart visualizations."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.visualization")
        self._graphs: dict[str, dict[str, Any]] = {}
        self._charts: dict[str, dict[str, Any]] = {}

    def register_graph(self, name: str, nodes: list[Any], edges: list[Any], **meta: Any) -> dict[str, Any]:
        graph = {"name": name, "nodes": nodes, "edges": edges, "meta": meta}
        self._graphs[name] = graph
        return graph

    def get_graph(self, name: str) -> dict[str, Any] | None:
        return self._graphs.get(name)

    def register_chart(self, name: str, kind: str, data: list[Any], **meta: Any) -> dict[str, Any]:
        chart = {"name": name, "kind": kind, "data": data, "meta": meta}
        self._charts[name] = chart
        return chart

    def get_chart(self, name: str) -> dict[str, Any] | None:
        return self._charts.get(name)

    def list(self) -> dict[str, list[str]]:
        return {"graphs": list(self._graphs), "charts": list(self._charts)}

    def neighbors(self, graph_name: str, node_id: str) -> list[str]:
        graph = self._graphs.get(graph_name)
        if graph is None:
            return []
        return [
            edge["target"] if edge.get("source") == node_id else edge["source"]
            for edge in graph["edges"]
            if edge.get("source") == node_id or edge.get("target") == node_id
        ]

    def clear(self) -> None:
        self._graphs.clear()
        self._charts.clear()
