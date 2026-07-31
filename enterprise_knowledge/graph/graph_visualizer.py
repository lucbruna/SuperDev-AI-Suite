"""Graph visualization: ASCII tree and Mermaid output."""

from __future__ import annotations

from typing import Any


class GraphVisualizer:
    """Renders the knowledge graph as ASCII or Mermaid."""

    def __init__(self, node_label_fn: Any = None,
                 neighbors_fn: Any = None) -> None:
        self._node_label_fn = node_label_fn or (lambda node_id: node_id)
        self._neighbors_fn = neighbors_fn

    def _neighbors(self, node_id: str) -> list[str]:
        if self._neighbors_fn is None:
            return []
        return [n["node_id"] for n in self._neighbors_fn(node_id)]

    # -- ASCII --------------------------------------------------------------
    def ascii_tree(self, root: str, max_depth: int = 3) -> str:
        lines: list[str] = []

        def walk(node_id: str, depth: int, seen: set[str]) -> None:
            if depth > max_depth:
                return
            prefix = "  " * depth + ("└─ " if depth else "")
            lines.append(f"{prefix}{self._node_label_fn(node_id)}")
            if node_id in seen:
                return
            seen = seen | {node_id}
            for neighbor in self._neighbors(node_id):
                walk(neighbor, depth + 1, seen)

        walk(root, 0, set())
        return "\n".join(lines)

    # -- Mermaid ------------------------------------------------------------
    def mermaid(self, edges: list[dict[str, Any]]) -> str:
        lines = ["graph TD"]
        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            rel = edge.get("rel_type", "-->")
            lines.append(f'    {source} -- "{rel}" --> {target}')
        return "\n".join(lines)

    def mermaid_nodes(self, nodes: list[dict[str, Any]]) -> str:
        lines = ["graph TD"]
        for node in nodes:
            node_id = node["node_id"]
            label = node.get("label", node_id)
            node_type = node.get("node_type", "concept")
            shape = "{" if node_type in {"project", "system", "company"} else "["
            close = "}" if shape == "{" else "]"
            lines.append(f"    {node_id}{shape}\"{label}\"{close}")
        return "\n".join(lines)
