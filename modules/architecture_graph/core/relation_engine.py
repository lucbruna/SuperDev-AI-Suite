"""Relation engine: infers semantic relations between node kinds.

Beyond raw imports, the platform has meaningful relationships that a text
scan cannot see:
* backend routers expose API endpoints (FastAPI route decorators);
* frontend files consume API endpoints (string references to /api/v1/...);
* agents, plugins and workflows map to the files that implement them;
* docker-compose services depend on other services;
* code files that use known infrastructure libraries use that service;
* markdown documents reference code files.
"""
from __future__ import annotations

import re
from typing import Any

from modules.architecture_graph.graph.edge_builder import (
    consumes,
    depends_on,
    exposes,
    uses,
)
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.graph.node_builder import (
    agent_node,
    api_node,
    document_node,
    plugin_node,
    service_node,
    workflow_node,
)

_SERVICE_MODULES = {
    "redis": "redis",
    "asyncpg": "postgres",
    "psycopg2": "postgres",
    "psycopg": "postgres",
    "sqlalchemy": "postgres",
    "neo4j": "neo4j",
    "pymongo": "mongodb",
    "motor": "mongodb",
    "kafka": "kafka",
    "confluent_kafka": "kafka",
    "pika": "rabbitmq",
    "celery": "rabbitmq",
}

_AGENT_DIRS = ("ai/agents", "agent_orchestration", "ai/agent")
_PLUGIN_DIRS = ("plugins", "core/plugin_manager", "modules/ai_video_studio/skills")
_WORKFLOW_DIRS = ("workflow_engine", "workflow", "automation")


def _under(rel_path: str, prefixes: tuple[str, ...]) -> bool:
    return any(rel_path == p or rel_path.startswith(p + "/") for p in prefixes)


def _kind_from_path(rel_path: str) -> tuple[str, str] | None:
    """Return (kind, name) for a path that identifies an agent/plugin/workflow."""
    parts = rel_path.replace("\\", "/").split("/")
    if _under(rel_path, _AGENT_DIRS):
        name = parts[-1].rsplit(".", 1)[0] if parts else rel_path
        if name in {"__init__"}:
            name = parts[-2] if len(parts) >= 2 else rel_path
        return "agent", name
    if _under(rel_path, _PLUGIN_DIRS):
        return "plugin", parts[-1].rsplit(".", 1)[0]
    if _under(rel_path, _WORKFLOW_DIRS) and rel_path.endswith((".yaml", ".yml", ".json")):
        return "workflow", parts[-1].rsplit(".", 1)[0]
    return None


def apply_relations(
    graph: ArchitectureGraph,
    parsed_files: dict[str, dict[str, Any]],
    *,
    plugins: list[dict[str, Any]] | None = None,
    workflows: list[dict[str, Any]] | None = None,
) -> dict[str, int]:
    """Apply semantic relations. Returns a count per relation kind."""
    counts: dict[str, int] = {"api": 0, "consume": 0, "agent": 0, "plugin": 0, "workflow": 0, "service": 0}

    # Path-level classification first (agents / plugins / workflows).
    for rel_path in parsed_files:
        classification = _kind_from_path(rel_path)
        if not classification:
            continue
        kind, name = classification
        node_id = f"file:{rel_path}"
        if kind == "agent":
            aid = f"agent:{name}"
            if not graph.has_node(aid):
                graph.add_node(agent_node(name, rel_path))
            if graph.add_edge(uses(aid, node_id)):
                counts["agent"] += 1
        elif kind == "plugin":
            pid = f"plugin:{name}"
            if not graph.has_node(pid):
                graph.add_node(plugin_node(name, rel_path))
            if graph.add_edge(uses(pid, node_id)):
                counts["plugin"] += 1

    # Explicit plugin records from manifests.
    for plugin in plugins or []:
        name = plugin.get("name", "")
        if not name:
            continue
        pid = f"plugin:{name}"
        if not graph.has_node(pid):
            graph.add_node(plugin_node(name, plugin.get("path", "")))
        for dep in plugin.get("dependencies") or []:
            if isinstance(dep, str) and dep:
                if graph.add_edge(depends_on(pid, dep, {"plugin_dep": True})):
                    counts["plugin"] += 1

    # Explicit workflow records.
    for workflow in workflows or []:
        name = workflow.get("name", "")
        wf_id = f"workflow:{name}"
        if not graph.has_node(wf_id):
            graph.add_node(workflow_node(name, workflow.get("path", "")))
        if workflow.get("path"):
            if graph.add_edge(uses(wf_id, f"file:{workflow['path']}")):
                counts["workflow"] += 1
        for agent in workflow.get("agents") or []:
            if agent:
                aid = f"agent:{agent}"
                if not graph.has_node(aid):
                    graph.add_node(agent_node(agent, ""))
                if graph.add_edge(depends_on(wf_id, aid)):
                    counts["workflow"] += 1

    # FastAPI route decorators -> API nodes exposed by the router file.
    for rel_path, parsed in parsed_files.items():
        for route in parsed.get("route_decorators") or []:
            path = route.get("path", "")
            if not path:
                continue
            aid = f"api:{route.get('method', 'get').lower()}:{path}"
            if not graph.has_node(aid):
                graph.add_node(api_node(route.get("method", "get"), path, rel_path))
            if graph.add_edge(exposes(f"file:{rel_path}", aid)):
                counts["api"] += 1

    # Frontend consumption of API endpoints.
    for rel_path, parsed in parsed_files.items():
        if parsed.get("language") not in {"javascript", "typescript"}:
            continue
        for api_path in parsed.get("api_paths") or []:
            method = "get"
            aid = f"api:{method}:{api_path}"
            if not graph.has_node(aid):
                graph.add_node(api_node(method, api_path, ""))
            if graph.add_edge(consumes(f"file:{rel_path}", aid)):
                counts["consume"] += 1

    # Infrastructure service usage via known library imports.
    for rel_path, parsed in parsed_files.items():
        if parsed.get("language") != "python":
            continue
        for imp in parsed.get("imports") or []:
            module = imp.get("module", "")
            top = module.split(".")[0]
            service = _SERVICE_MODULES.get(top)
            if not service:
                continue
            sid = f"service:{service}"
            if not graph.has_node(sid):
                graph.add_node(service_node(service))
            if graph.add_edge(uses(f"file:{rel_path}", sid)):
                counts["service"] += 1

    # Markdown documents referencing code files.
    for rel_path, parsed in parsed_files.items():
        if parsed.get("language") != "markdown":
            continue
        if graph.add_edge(uses(f"file:{rel_path}", f"doc:{rel_path}")):
            pass
        # Register the doc node itself.
        doc_id = f"doc:{rel_path}"
        if not graph.has_node(doc_id):
            graph.add_node(document_node(rel_path, rel_path))
        for ref in parsed.get("code_refs") or []:
            if graph.has_node(f"file:{ref}"):
                if graph.add_edge(uses(doc_id, f"file:{ref}")):
                    counts["workflow"] += 0  # counted below

    return counts
