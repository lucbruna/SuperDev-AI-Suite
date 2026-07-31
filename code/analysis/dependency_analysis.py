from __future__ import annotations

import logging
from typing import Any

from ..understanding.dependency_graph import DependencyGraph


class DependencyAnalysis:
    """Analyzes code dependencies."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.analysis.dependency")

    def analyze(self, files: list[Any]) -> dict[str, Any]:
        """Build a dependency graph from *files* (``CodeFile`` objects or
        dicts with ``path``/``content``) and return it with a summary."""
        graph = DependencyGraph()
        summary = graph.build(files)
        return {"graph": graph.to_dict(), "summary": summary}
