"""Defined intelligence agents (scoped reviewers/planners).

Each agent inspects the graph or the engine and returns a small report dict.
They are orchestrated by AgentManager; none of them require an LLM.
"""
from __future__ import annotations

from typing import Any, Callable

from modules.architecture_graph.analytics.complexity_analyzer import hotspots
from modules.architecture_graph.analytics.coupling_analyzer import hot_couples
from modules.architecture_graph.dependency.circular_detector import find_cycles
from modules.architecture_graph.dependency.dead_code_detector import find_dead_files
from modules.architecture_graph.dependency.orphan_detector import find_orphans


def complexity_agent(graph: Any) -> dict[str, Any]:
    hot = hotspots(graph, top=10)
    return {
        "name": "complexity",
        "summary": f"Top {len(hot)} hotspots by complexity.",
        "items": [{"node": h.get("node"), "score": h.get("score")} for h in hot[:10]],
    }


def coupling_agent(graph: Any) -> dict[str, Any]:
    couples = hot_couples(graph, top=10)
    return {
        "name": "coupling",
        "summary": f"Top {len(couples)} hot couples.",
        "items": [{"source": c.get("source"), "target": c.get("target")} for c in couples[:10]],
    }


def _cycle_parts(cycle: Any) -> list[str]:
    if isinstance(cycle, list):
        return [str(x) for x in cycle]
    return [str(cycle)]


def cycles_agent(graph: Any) -> dict[str, Any]:
    cycles = find_cycles(graph)
    items = [{"cycle": _cycle_parts(c)[:8]} for c in cycles[:10]]
    return {
        "name": "cycles",
        "summary": f"{len(cycles)} dependency cycles found.",
        "items": items,
    }


def dead_code_agent(graph: Any) -> dict[str, Any]:
    dead = find_dead_files(graph)
    return {
        "name": "dead_code",
        "summary": f"{len(dead)} dead files detected.",
        "items": [{"file": d} for d in dead[:20]],
    }


def orphans_agent(graph: Any) -> dict[str, Any]:
    orphans = find_orphans(graph)
    return {
        "name": "orphans",
        "summary": f"{len(orphans)} orphan nodes.",
        "items": [{"node": o} for o in orphans[:20]],
    }


def _documents_agent(graph: Any) -> dict[str, Any]:
    stats = graph.stats()
    return {
        "name": "documentation",
        "summary": (
            f"{stats.get('nodes', 0)} nodes, {stats.get('edges', 0)} edges, "
            f"{stats.get('packages', 0)} packages."
        ),
        "items": [{"stat": k, "value": v} for k, v in sorted(stats.items())],
    }


AGENTS: dict[str, Callable[[Any], dict[str, Any]]] = {
    "complexity": complexity_agent,
    "coupling": coupling_agent,
    "cycles": cycles_agent,
    "dead_code": dead_code_agent,
    "orphans": orphans_agent,
    "documentation": _documents_agent,
}
