from __future__ import annotations

import logging
from collections import deque
from typing import Any

from .dependency_graph import DependencyGraph


def estimate_tokens(text: str) -> int:
    """Rough token estimate (heuristic: ~4 chars per token)."""
    return max(1, len(text) // 4)


class ContextBuilder:
    """Selects relevant files for an LLM prompt using BFS on the dependency
    graph, starting from seed files.

    BFS walks edges in both directions (dependencies and dependents), so a
    seed file pulls in both the modules it imports and the modules that
    import it. Selection is bounded by ``max_depth``, ``max_files`` and a
    ``max_tokens`` budget (seed files are always kept).
    """

    def __init__(self, max_depth: int = 3, max_files: int = 8,
                 max_tokens: int = 8000) -> None:
        self.max_depth = max(0, max_depth)
        self.max_files = max(1, max_files)
        self.max_tokens = max(1, max_tokens)
        self._log = logging.getLogger("superdev.code.understanding.context")

    def build(
        self,
        seed_files: list[str],
        graph: DependencyGraph,
        files_by_path: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Run BFS from *seed_files* over *graph*.

        *files_by_path* optionally maps path -> content so the returned
        selection can be injected straight into a prompt. Returns a dict with
        ``selected`` (list of ``{"path", "depth", "tokens"}``), ``files``
        (ordered paths) and ``total_tokens``.
        """
        files_by_path = files_by_path or {}
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque()
        for seed in seed_files:
            if seed not in visited:
                visited.add(seed)
                queue.append((seed, 0))

        selected: list[dict[str, Any]] = []
        total_tokens = 0
        while queue and len(selected) < self.max_files:
            node, depth = queue.popleft()
            if depth > self.max_depth:
                continue

            tokens = estimate_tokens(files_by_path.get(node, ""))
            is_seed = depth == 0 and node in seed_files
            if not is_seed and total_tokens + tokens > self.max_tokens:
                continue

            selected.append({"path": node, "depth": depth, "tokens": tokens})
            total_tokens += tokens

            if depth >= self.max_depth:
                continue
            for neighbor in (*graph.get_dependencies(node),
                             *graph.get_dependents(node)):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))

        return {"selected": selected,
                "files": [entry["path"] for entry in selected],
                "total_tokens": total_tokens,
                "budget": {"max_files": self.max_files,
                           "max_tokens": self.max_tokens}}
