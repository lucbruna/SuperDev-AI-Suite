"""Permission mapper: map permission systems onto the architecture graph.

Discovers RBAC/permission definitions (roles, capabilities, guards) across the
backend and registers them as nodes with their access relations, so security
topology is visible in the same graph as the rest of the architecture.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from modules.architecture_graph.graph.edge_builder import exposes, uses
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.graph.node_builder import config_node

_CAPABILITY_RE = re.compile(r"(?:require|can|has_capability|permission)\s*[:=]\s*[\"']?([a-z0-9_.-]+)", re.IGNORECASE)
_ROLE_DIRS = ("backend/auth", "backend/rbac", "security", "core/security")


def _discover_permissions(root: str) -> list[dict[str, Any]]:
    base = Path(root)
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for directory in [base / d for d in _ROLE_DIRS if (base / d).exists()]:
        for entry in sorted(directory.rglob("*.py")):
            rel = entry.relative_to(base).as_posix()
            if rel in seen:
                continue
            seen.add(rel)
            try:
                text = entry.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            capabilities = sorted(set(_CAPABILITY_RE.findall(text)))
            if not capabilities:
                continue
            records.append(
                {
                    "path": rel,
                    "capabilities": capabilities,
                    "count": len(capabilities),
                }
            )
    return records


class PermissionMapper:
    """Maps permission/RBAC definitions onto the graph."""

    def __init__(self, root: str) -> None:
        self.root = root
        self.records: list[dict[str, Any]] = []

    def discover(self) -> list[dict[str, Any]]:
        self.records = _discover_permissions(self.root)
        return self.records

    def apply(self, graph: ArchitectureGraph) -> int:
        """Register permission source nodes and capability edges."""
        if not self.records:
            self.discover()
        added = 0
        for record in self.records:
            rel = record.get("path", "")
            if not rel:
                continue
            node_id = f"config:{rel}"
            if not graph.has_node(node_id):
                node = config_node(f"permissions:{rel}", rel)
                node.meta = {"capabilities": record.get("capabilities", [])}
                graph.add_node(node)
                added += 1
            # Permissions guard the API routes they're declared next to.
            if "/api/" in rel:
                route = rel.split("/api/", 1)[1].rsplit(".py", 1)[0].replace("/", ":")
                if graph.has_node(f"api:{route}"):
                    graph.add_edge(exposes(node_id, f"api:{route}"))
        return added

    def summary(self) -> dict[str, Any]:
        if not self.records:
            self.discover()
        total_caps = sum(r.get("count", 0) for r in self.records)
        return {
            "files": len(self.records),
            "capabilities": total_caps,
            "sources": [r.get("path") for r in self.records],
        }


def discover_permissions(root: str) -> list[dict[str, Any]]:
    """One-shot convenience helper."""
    return _discover_permissions(root)
