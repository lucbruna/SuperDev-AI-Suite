from __future__ import annotations

import logging
from typing import Any

from .dependency_graph import DependencyGraph
from .symbol_index import SymbolIndex


class CodeUnderstanding:
    """Understands codebase structure and semantics."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.understanding")

    def understand(self, path: str) -> dict[str, Any]:
        """Scan *path* and build the symbol index + dependency graph.

        Returns a dict with ``files`` (count), ``symbols`` (index mapping),
        ``symbol_count``, ``graph`` (dependency edges) and ``graph_summary``.
        """
        from ..code_scanner import CodeScanner

        self._log.info("Understanding codebase at %s", path)
        files = CodeScanner().scan(path)

        symbols = SymbolIndex()
        symbols.index_files(files)

        graph = DependencyGraph()
        graph_summary = graph.build(files)

        return {
            "files": len(files),
            "symbols": symbols.to_dict(),
            "symbol_count": symbols.count(),
            "graph": graph.to_dict(),
            "graph_summary": graph_summary,
        }
