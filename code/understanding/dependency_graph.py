from __future__ import annotations

import logging
from typing import Any

from ..parsing.ast_manager import ASTManager


class DependencyGraph:
    """Builds and queries dependency graphs derived from source imports.

    Nodes are file paths; an edge ``A -> B`` means file ``A`` imports module
    ``B``. ``build`` parses a collection of files with :class:`ASTManager`
    and adds the edges automatically.
    """

    def __init__(self, ast_manager: ASTManager | None = None) -> None:
        self._graph: dict[str, list[str]] = {}
        self._ast = ast_manager or ASTManager()
        self._log = logging.getLogger("superdev.code.understanding.deps")

    def add(self, node: str, depends_on: str) -> None:
        """Register a ``node -> depends_on`` edge (deduplicated)."""
        deps = self._graph.setdefault(node, [])
        if depends_on not in deps:
            deps.append(depends_on)

    def get_dependencies(self, node: str) -> list[str]:
        """Modules imported by *node* (direct edges)."""
        return self._graph.get(node, [])

    def get_dependents(self, node: str) -> list[str]:
        """Files that import *node* (reverse edges)."""
        return [src for src, deps in self._graph.items() if node in deps]

    def nodes(self) -> list[str]:
        """All registered node names."""
        return list(self._graph)

    def edges(self) -> list[tuple[str, str]]:
        """All ``(source, dependency)`` edges."""
        return [(src, dep) for src, deps in self._graph.items()
                for dep in deps]

    def build(self, files: list[Any]) -> dict[str, Any]:
        """Parse *files* and add ``path -> imported-module`` edges.

        *files* may be ``CodeFile`` objects or dicts with ``path``/``content``
        keys. Files with syntax errors are skipped and reported in the
        returned summary under ``errors``.
        """
        summary = {"files": len(files), "parsed": 0, "errors": []}
        for file in files:
            if isinstance(file, dict):
                content = file.get("content", "")
                path = file.get("path", "")
            else:
                content = getattr(file, "content", "")
                path = getattr(file, "path", "")

            parsed = self._ast.parse(content or "")
            if parsed is None:
                summary["errors"].append({"path": path,
                                          "error": "syntax_error"})
                continue

            summary["parsed"] += 1
            for imp in parsed["imports"]:
                self.add(path, imp["module"])

        summary["nodes"] = len(self.nodes())
        summary["edges"] = len(self.edges())
        return summary

    def to_dict(self) -> dict[str, Any]:
        """Serializable mapping of ``node -> [dependencies]``."""
        return {node: list(deps) for node, deps in self._graph.items()}
