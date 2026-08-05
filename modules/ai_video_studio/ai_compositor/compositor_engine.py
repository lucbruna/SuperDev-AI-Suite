"""Compositing engine — renders node graphs into final frames.

Nodes are function objects operating on float frames ``(H, W, 3)``.
A graph is a dict ``{node_id: (op, inputs: dict[name, node_id|frame])}``.
"""
from __future__ import annotations

from typing import Any, Callable

import numpy as np
from numpy.typing import NDArray


class NodeGraphError(RuntimeError):
    """Raised when a node graph cannot be evaluated."""


NodeOp = Callable[[dict[str, NDArray[np.floating]], dict[str, Any]], NDArray[np.floating]]


class CompositorEngine:
    """Evaluates node graphs with memoized execution + cycle detection."""

    def __init__(self) -> None:
        self._nodes: dict[str, NodeOp] = {}
        self._inputs: dict[str, dict[str, Any]] = {}

    def register(self, name: str, op: NodeOp) -> None:
        self._nodes[name] = op

    def graph(self, g: dict[str, tuple[str, dict[str, Any]]]) -> None:
        """Set the current graph. ``g`` maps id -> (node_name, params)."""
        for node_id, (node_name, params) in g.items():
            if node_name not in self._nodes:
                raise NodeGraphError(f"unknown node {node_name!r}")
        self._inputs = g

    def evaluate(self, g: dict[str, tuple[str, dict[str, Any]]] | None = None) -> NDArray[np.floating]:
        """Evaluate the graph's primary output node (id ``'output'`` if present)."""
        graph = g or self._inputs
        if not graph:
            raise NodeGraphError("empty graph")
        out_id = "output" if "output" in graph else list(graph)[-1]
        memo: dict[str, NDArray[np.floating]] = {}
        visiting: set[str] = set()

        def eval_node(node_id: str) -> NDArray[np.floating]:
            if node_id in memo:
                return memo[node_id]
            if node_id in visiting:
                raise NodeGraphError(f"cycle detected at node {node_id!r}")
            visiting.add(node_id)
            name, params = graph[node_id]
            op = self._nodes[name]
            feeds: dict[str, NDArray[np.floating]] = {}
            for k, v in params.items():
                if isinstance(v, str) and v in graph:
                    feeds[k] = eval_node(v)
            out = op(feeds, {k: v for k, v in params.items() if not (isinstance(v, str) and v in graph)})
            visiting.discard(node_id)
            memo[node_id] = out
            return out

        return eval_node(out_id)

    def clear(self) -> None:
        self._inputs = {}

    def current_graph(self) -> dict[str, tuple[str, dict[str, Any]]]:
        """Return the currently configured graph (id -> (node_name, params))."""
        return self._inputs

    def stats(self) -> dict:
        return {"nodes": len(self._nodes), "graph": len(self._inputs)}
