from __future__ import annotations

import logging


class DependencyGraph:
    """Builds and queries dependency graphs."""

    def __init__(self) -> None:
        self._graph: dict[str, list[str]] = {}
        self._log = logging.getLogger("superdev.code.understanding.deps")

    def add(self, node: str, depends_on: str) -> None:
        self._graph.setdefault(node, []).append(depends_on)

    def get_dependencies(self, node: str) -> list[str]:
        return self._graph.get(node, [])
