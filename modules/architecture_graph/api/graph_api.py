"""Graph API: lifecycle and query endpoints for the architecture graph."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from modules.architecture_graph.api.deps import get_optional_user
from modules.architecture_graph.core.architecture_engine import get_engine
from modules.architecture_graph.exports.reactflow import to_reactflow
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph

router = APIRouter(tags=["Architecture Graph"])


@router.get("/")
async def graph_status(user: dict[str, Any] = Depends(get_optional_user)) -> dict[str, Any]:
    """Current graph state: stats, last build info, availability."""
    engine = get_engine()
    graph = engine.load()
    if graph is None:
        return {"available": False, "message": "Graph not built yet. POST /build to scan."}
    return {
        "available": True,
        "stats": graph.stats(),
        "last_build": engine.last_build,
    }


@router.post("/build")
async def build_graph(user: dict[str, Any] = Depends(get_optional_user)) -> dict[str, Any]:
    """Full scan + parse + build + persist."""
    engine = get_engine()
    try:
        graph = engine.build()
    except Exception as exc:  # defensive
        raise HTTPException(status_code=500, detail=f"Build failed: {exc}") from exc
    return {"ok": True, "stats": graph.stats(), "last_build": engine.last_build}


@router.post("/refresh")
async def refresh_graph(user: dict[str, Any] = Depends(get_optional_user)) -> dict[str, Any]:
    """Incremental refresh based on file snapshot diff."""
    engine = get_engine()
    try:
        result = engine.refresh()
    except Exception as exc:  # defensive
        raise HTTPException(status_code=500, detail=f"Refresh failed: {exc}") from exc
    return {"ok": True, **result}


@router.get("/graph")
async def graph_payload(
    fmt: str = Query("reactflow", pattern="^(reactflow|cytoscape|graphviz|mermaid|svg|html)$"),
    user: dict[str, Any] = Depends(get_optional_user),
) -> dict[str, Any]:
    """Return the graph in a serializable format for the frontend."""
    engine = get_engine()
    graph = engine.ensure_graph()
    if graph is None:
        raise HTTPException(status_code=404, detail="Graph not available")
    if fmt == "reactflow":
        return {"format": "reactflow", **to_reactflow(graph)}
    if fmt == "cytoscape":
        from modules.architecture_graph.exports.cytoscape import to_cytoscape

        return {"format": "cytoscape", **to_cytoscape(graph)}
    if fmt == "graphviz":
        from modules.architecture_graph.exports.graphviz import to_dot

        return {"format": "graphviz", "source": to_dot(graph)}
    if fmt == "mermaid":
        from modules.architecture_graph.exports.mermaid import to_mermaid

        return {"format": "mermaid", "source": to_mermaid(graph)}
    if fmt == "svg":
        from modules.architecture_graph.exports.svg import to_svg

        return {"format": "svg", "source": to_svg(graph)}
    from modules.architecture_graph.exports.html import to_html

    return {"format": "html", "source": to_html(graph)}


@router.get("/nodes")
async def list_nodes(
    kind: str | None = Query(None),
    layer: str | None = Query(None),
    query: str | None = Query(None),
    limit: int = Query(200, ge=1, le=5000),
    user: dict[str, Any] = Depends(get_optional_user),
) -> dict[str, Any]:
    """List graph nodes with optional filters."""
    engine = get_engine()
    graph = engine.ensure_graph()
    if graph is None:
        raise HTTPException(status_code=404, detail="Graph not available")
    nodes = graph.nodes()
    if kind:
        nodes = [n for n in nodes if n.kind == kind]
    if layer:
        nodes = [n for n in nodes if n.layer == layer]
    if query:
        nodes = graph.nodes_matching(query)
    nodes.sort(key=lambda n: (n.kind, n.id))
    return {"total": len(nodes), "nodes": [n.to_dict() for n in nodes[:limit]]}


@router.get("/nodes/{node_id}")
async def get_node(node_id: str, user: dict[str, Any] = Depends(get_optional_user)) -> dict[str, Any]:
    """Node detail with neighbors, dependents and dependencies."""
    engine = get_engine()
    graph = engine.ensure_graph()
    if graph is None:
        raise HTTPException(status_code=404, detail="Graph not available")
    node = graph.get_node(node_id)
    if node is None:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
    return {
        "node": node.to_dict(),
        "dependents": graph.incoming(node_id),
        "dependencies": graph.outgoing(node_id),
        "neighbors": graph.neighbors(node_id),
    }


@router.get("/edges")
async def list_edges(
    kind: str | None = Query(None),
    limit: int = Query(500, ge=1, le=10000),
    user: dict[str, Any] = Depends(get_optional_user),
) -> dict[str, Any]:
    """List graph edges with optional kind filter."""
    engine = get_engine()
    graph = engine.ensure_graph()
    if graph is None:
        raise HTTPException(status_code=404, detail="Graph not available")
    edges = graph.edges_of(kind) if kind else graph.edges()
    return {"total": len(edges), "edges": [e.to_dict() for e in edges[:limit]]}


@router.get("/impact/{node_id}")
async def impact(node_id: str, user: dict[str, Any] = Depends(get_optional_user)) -> dict[str, Any]:
    """Blast-radius analysis for a node."""
    engine = get_engine()
    result = engine.impact(node_id)
    if not result.get("available", True):
        raise HTTPException(status_code=404, detail="Graph not available")
    if not result.get("found", True):
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
    return result
