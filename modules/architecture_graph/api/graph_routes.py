"""Graph routes: analysis, AI, exports and reports endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from modules.architecture_graph.ai.architecture_ai import get_ai
from modules.architecture_graph.api.deps import get_optional_user
from modules.architecture_graph.core.architecture_engine import get_engine
from modules.architecture_graph.core.metrics_engine import graph_metrics, module_metrics

router = APIRouter(tags=["Architecture Graph — Analysis"])


@router.get("/metrics")
async def metrics(user: dict[str, Any] = Depends(get_optional_user)) -> dict[str, Any]:
    """Graph-level metrics (density, coupling, complexity summary)."""
    engine = get_engine()
    graph = engine.ensure_graph()
    if graph is None:
        raise HTTPException(status_code=404, detail="Graph not available")
    return {"graph": graph_metrics(graph), "modules": module_metrics(graph)[:50]}


@router.get("/analyze")
async def analyze(user: dict[str, Any] = Depends(get_optional_user)) -> dict[str, Any]:
    """Full analysis: score, layers, cycles, integrity, metrics."""
    engine = get_engine()
    result = engine.analyze()
    if not result.get("available", True):
        raise HTTPException(status_code=404, detail="Graph not available")
    return result


@router.get("/insights")
async def insights(user: dict[str, Any] = Depends(get_optional_user)) -> dict[str, Any]:
    """Ranked AI insights over the graph."""
    ai = get_ai()
    result = ai.insights()
    if not result.get("available", True):
        raise HTTPException(status_code=404, detail="Graph not available")
    return result


@router.get("/insights/risk")
async def risk_ranking(
    limit: int = Query(10, ge=1, le=100),
    user: dict[str, Any] = Depends(get_optional_user),
) -> dict[str, Any]:
    """Highest-risk nodes."""
    ai = get_ai()
    result = ai.risk_ranking(limit=limit)
    if not result.get("available", True):
        raise HTTPException(status_code=404, detail="Graph not available")
    return result


@router.get("/plan")
async def plan(user: dict[str, Any] = Depends(get_optional_user)) -> dict[str, Any]:
    """Improvement plan derived from the current graph."""
    ai = get_ai()
    result = ai.plan()
    if not result.get("available", True):
        raise HTTPException(status_code=404, detail="Graph not available")
    return result


@router.post("/plan/migration")
async def migration_plan(
    body: dict[str, Any],
    user: dict[str, Any] = Depends(get_optional_user),
) -> dict[str, Any]:
    """Plan a migration of nodes into a target package."""
    target = body.get("target_package", "")
    if not target:
        raise HTTPException(status_code=422, detail="target_package is required")
    ai = get_ai()
    result = ai.migration_plan(target, nodes=body.get("nodes"))
    if not result.get("available", True):
        raise HTTPException(status_code=404, detail="Graph not available")
    return result


@router.get("/explain/{node_id}")
async def explain(node_id: str, user: dict[str, Any] = Depends(get_optional_user)) -> dict[str, Any]:
    """Natural-language explanation for a node."""
    ai = get_ai()
    result = ai.explain(node_id)
    if not result.get("available", True) and "text" not in result:
        raise HTTPException(status_code=404, detail="Graph not available")
    return result


@router.get("/search")
async def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    user: dict[str, Any] = Depends(get_optional_user),
) -> dict[str, Any]:
    """Semantic-ish search over graph nodes."""
    ai = get_ai()
    result = ai.search(q, limit=limit)
    if not result.get("available", True):
        raise HTTPException(status_code=404, detail="Graph not available")
    return result


@router.get("/related/{node_id}")
async def related(
    node_id: str,
    limit: int = Query(5, ge=1, le=20),
    user: dict[str, Any] = Depends(get_optional_user),
) -> dict[str, Any]:
    """Nodes most similar to a given node."""
    ai = get_ai()
    result = ai.related(node_id, limit=limit)
    if not result.get("available", True):
        raise HTTPException(status_code=404, detail="Graph not available")
    return result


@router.get("/export/{fmt}")
async def export_graph(
    fmt: str,
    user: dict[str, Any] = Depends(get_optional_user),
) -> Any:
    """Export the graph in the requested format."""
    if fmt not in {"reactflow", "cytoscape", "graphviz", "mermaid", "svg", "html", "png", "pdf"}:
        raise HTTPException(status_code=422, detail=f"Unsupported format: {fmt}")
    from fastapi.responses import JSONResponse, Response

    engine = get_engine()
    graph = engine.ensure_graph()
    if graph is None:
        raise HTTPException(status_code=404, detail="Graph not available")

    if fmt == "reactflow":
        from modules.architecture_graph.exports.reactflow import to_json

        return Response(to_json(graph), media_type="application/json")
    if fmt == "cytoscape":
        from modules.architecture_graph.exports.cytoscape import to_json

        return Response(to_json(graph), media_type="application/json")
    if fmt == "graphviz":
        from modules.architecture_graph.exports.graphviz import to_dot

        return Response(to_dot(graph), media_type="text/vnd.graphviz")
    if fmt == "mermaid":
        from modules.architecture_graph.exports.mermaid import to_mermaid

        return Response(to_mermaid(graph), media_type="text/plain")
    if fmt == "svg":
        from modules.architecture_graph.exports.svg import to_svg

        return Response(to_svg(graph), media_type="image/svg+xml")
    if fmt == "html":
        from modules.architecture_graph.exports.html import to_html

        return Response(to_html(graph), media_type="text/html")
    if fmt == "png":
        from modules.architecture_graph.exports.png import to_png

        result = to_png(graph)
        if result.get("rendered"):
            return Response(bytes(result["data"]), media_type="image/png")
        return JSONResponse(status_code=503, content=result)
    from modules.architecture_graph.exports.png import to_pdf

    result = to_pdf(graph)
    if result.get("rendered"):
        return Response(bytes(result["data"]), media_type="application/pdf")
    return JSONResponse(status_code=503, content=result)


@router.get("/reports/{kind}")
async def report(
    kind: str,
    user: dict[str, Any] = Depends(get_optional_user),
) -> dict[str, Any]:
    """Generated reports (markdown/html)."""
    if kind not in {"architecture", "dependency", "documentation", "html"}:
        raise HTTPException(status_code=422, detail=f"Unsupported report: {kind}")
    engine = get_engine()
    graph = engine.ensure_graph()
    if graph is None:
        raise HTTPException(status_code=404, detail="Graph not available")
    if kind == "architecture":
        from modules.architecture_graph.reports.architecture_report import (
            ArchitectureReport,
        )

        return ArchitectureReport().to_dict(graph)
    if kind == "dependency":
        from modules.architecture_graph.reports.dependency_report import (
            DependencyReport,
        )

        return DependencyReport().to_dict(graph)
    if kind == "documentation":
        from modules.architecture_graph.reports.documentation_generator import (
            DocumentationGenerator,
        )

        return {"format": "markdown", "title": "Architecture Documentation", "source": DocumentationGenerator().generate(graph)}
    from modules.architecture_graph.reports.html_report import to_dict as html_to_dict

    return html_to_dict(graph)
