"""Integrity engine: structural and consistency issues in the graph."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.graph.graph_validator import validate


def check(
    graph: ArchitectureGraph, parsed_files: dict[str, dict[str, Any]] | None = None
) -> list[dict[str, Any]]:
    """Return a list of integrity issues found in the graph + parses."""
    issues: list[dict[str, Any]] = list(validate(graph))

    parsed_files = parsed_files or {}
    for rel_path, parsed in parsed_files.items():
        if parsed.get("error"):
            issues.append(
                {
                    "type": "syntax_error",
                    "path": rel_path,
                    "detail": parsed["error"],
                }
            )
        if parsed.get("language") == "python":
            for route in parsed.get("route_decorators") or []:
                path = route.get("path", "")
                if path and not path.startswith("/"):
                    issues.append(
                        {
                            "type": "relative_route",
                            "path": rel_path,
                            "detail": f"route {path!r} does not start with '/'",
                        }
                    )
        for imp in parsed.get("imports") or []:
            module = imp.get("module", "")
            if module and module.endswith(("..", ".py")):
                issues.append(
                    {
                        "type": "malformed_import",
                        "path": rel_path,
                        "detail": module,
                    }
                )

    for node in graph.nodes():
        if node.kind == "file" and node.size == 0:
            issues.append({"type": "empty_file", "path": node.path, "detail": node.name})

    return issues


def summary(issues: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for issue in issues:
        key = issue.get("type", "unknown")
        counts[key] = counts.get(key, 0) + 1
    return counts
