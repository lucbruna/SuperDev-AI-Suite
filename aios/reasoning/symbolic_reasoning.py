"""AIOS Symbolic Reasoning — knowledge-graph style inference.

Builds a directed symbol graph from premises (subject -> relation ->
object) and answers reachability queries over symbols.
"""

from __future__ import annotations

from typing import Any


class SymbolicReasoning:
    """Graph-based symbolic reasoning over triples."""

    def __init__(self) -> None:
        self._edges: dict[str, list[tuple[str, str]]] = {}  # subject -> [(relation, object)]

    def reason(self, premises: list[Any], **kwargs: Any) -> dict[str, Any]:
        for premise in premises:
            if isinstance(premise, dict) and "subject" in premise and "object" in premise:
                self._edges.setdefault(str(premise["subject"]), []).append(
                    (str(premise.get("relation", "related_to")), str(premise["object"]))
                )
        query = kwargs.get("query")
        reachable: dict[str, list[str]] = {}
        if query is not None:
            start = str(query)
            visited: set[str] = set()
            stack = [start]
            while stack:
                node = stack.pop()
                if node in visited:
                    continue
                visited.add(node)
                for _rel, obj in self._edges.get(node, []):
                    if obj not in visited:
                        stack.append(obj)
            reachable[start] = sorted(visited - {start})
        return {
            "ok": True,
            "strategy": "symbolic",
            "nodes": sorted(self._edges.keys()),
            "reachable": reachable,
        }
