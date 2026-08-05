"""Factories for creating typed graph nodes with consistent ids.

Node ids are deterministic (path-derived or slug-derived) so that repeated
scans produce stable graphs that can be diffed across builds.
"""
from __future__ import annotations

import re
from typing import Any

from modules.architecture_graph.graph.graph_builder import GraphNode, layer_of

_SLUG_RE = re.compile(r"[^a-zA-Z0-9_./\-]")


def _slug(text: str) -> str:
    return _SLUG_RE.sub("_", text).strip("_")


def _file_id(rel_path: str) -> str:
    rel_path = rel_path.replace("\\", "/")
    return "file:" + rel_path


def file_node(
    rel_path: str,
    *,
    language: str = "",
    size: int = 0,
    meta: dict[str, Any] | None = None,
) -> GraphNode:
    rel_path = rel_path.replace("\\", "/")
    return GraphNode(
        id=_file_id(rel_path),
        name=rel_path.rsplit("/", 1)[-1],
        kind="file",
        language=language,
        path=rel_path,
        size=size,
        layer=layer_of(rel_path),
        meta=meta or {},
    )


def package_node(name: str, rel_path: str) -> GraphNode:
    rel_path = rel_path.replace("\\", "/")
    # Normalize the id: drop trailing slashes so `package:{dir}` ids stay
    # stable whether callers pass "src" or "src/".
    slug_source = rel_path.rstrip("/") or name
    return GraphNode(
        id=f"package:{_slug(slug_source)}",
        name=name,
        kind="package",
        path=rel_path,
        layer=layer_of(rel_path),
    )


def module_node(name: str, rel_path: str = "") -> GraphNode:
    rel_path = rel_path.replace("\\", "/")
    return GraphNode(
        id=f"module:{_slug(name)}",
        name=name,
        kind="module",
        path=rel_path,
        layer=layer_of(rel_path) or "modules",
        meta={"module_dir": rel_path},
    )


def api_node(method: str, route: str, owner_path: str = "") -> GraphNode:
    """API endpoint node. ``route`` is the full path (e.g. /api/v1/users)."""
    route = route.replace("\\", "/")
    return GraphNode(
        id=f"api:{method.lower()}:{route}",
        name=f"{method.upper()} {route}",
        kind="api",
        path=owner_path,
        layer=layer_of(owner_path) or "backend",
        meta={"method": method.upper(), "route": route},
    )


def class_node(name: str, owner_path: str = "", language: str = "") -> GraphNode:
    return GraphNode(
        id=f"class:{_slug(name)}",
        name=name,
        kind="class",
        language=language,
        path=owner_path,
    )


def function_node(name: str, owner_path: str = "", language: str = "") -> GraphNode:
    return GraphNode(
        id=f"func:{_slug(name)}",
        name=name,
        kind="function",
        language=language,
        path=owner_path,
    )


def agent_node(name: str, rel_path: str = "") -> GraphNode:
    return GraphNode(
        id=f"agent:{_slug(name)}",
        name=name,
        kind="agent",
        path=rel_path.replace("\\", "/"),
        layer="ai",
    )


def plugin_node(name: str, rel_path: str = "") -> GraphNode:
    return GraphNode(
        id=f"plugin:{_slug(name)}",
        name=name,
        kind="plugin",
        path=rel_path.replace("\\", "/"),
    )


def workflow_node(name: str, rel_path: str = "") -> GraphNode:
    return GraphNode(
        id=f"workflow:{_slug(name)}",
        name=name,
        kind="workflow",
        path=rel_path.replace("\\", "/"),
        layer="workflow_engine",
    )


def service_node(name: str, kind: str = "service") -> GraphNode:
    """External infrastructure service (redis, postgres, neo4j, ...)."""
    return GraphNode(
        id=f"service:{_slug(name)}",
        name=name,
        kind="service",
        layer="infrastructure",
        meta={"service": kind},
    )


def database_node(name: str) -> GraphNode:
    return GraphNode(id=f"database:{_slug(name)}", name=name, kind="database", layer="infrastructure")


def external_node(name: str) -> GraphNode:
    """Third-party dependency node (pip/npm package)."""
    return GraphNode(
        id=f"external:{_slug(name)}",
        name=name,
        kind="external",
        layer="external",
        meta={"external": True},
    )


def config_node(name: str, rel_path: str = "") -> GraphNode:
    return GraphNode(
        id=f"config:{_slug(name)}",
        name=name,
        kind="config",
        path=rel_path.replace("\\", "/"),
    )


def document_node(name: str, rel_path: str = "") -> GraphNode:
    return GraphNode(
        id=f"doc:{_slug(rel_path or name)}",
        name=name,
        kind="document",
        path=rel_path.replace("\\", "/"),
        layer="docs",
    )
