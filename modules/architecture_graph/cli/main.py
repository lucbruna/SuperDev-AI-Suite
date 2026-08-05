"""CLI entry point for the Architecture Graph module.

Usage::

    python -m modules.architecture_graph.cli build [--no-persist]
    python -m modules.architecture_graph.cli refresh
    python -m modules.architecture_graph.cli analyze
    python -m modules.architecture_graph.cli nodes [--kind file] [--limit 50]
    python -m modules.architecture_graph.cli impact <node_id>
    python -m modules.architecture_graph.cli export <fmt> [--out path]
    python -m modules.architecture_graph.cli report <kind> [--out path]
    python -m modules.architecture_graph.cli serve [--port 8000]

All commands degrade gracefully when the graph cannot be built (missing
dependencies, no scan sources) by reporting an error instead of crashing.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from modules.architecture_graph.core.architecture_engine import get_engine
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


def _graph(args: argparse.Namespace) -> ArchitectureGraph:
    engine = get_engine()
    graph = engine.ensure_graph(build_if_missing=not args.no_build)
    if graph is None:
        raise SystemExit("Graph not available. Run 'build' first or pass --build.")
    return graph


# --------------------------------------------------------------------- build
def cmd_build(args: argparse.Namespace) -> int:
    engine = get_engine()
    graph = engine.build(persist=not args.no_persist)
    print(json.dumps({"ok": True, "stats": graph.stats()}, indent=2))
    return 0


def cmd_refresh(args: argparse.Namespace) -> int:
    engine = get_engine()
    result = engine.refresh()
    print(json.dumps({"ok": True, **result}, indent=2))
    return 0


# --------------------------------------------------------------- query/analyze
def cmd_analyze(args: argparse.Namespace) -> int:
    result = get_engine().analyze()
    if not result.get("available", True):
        raise SystemExit("Graph not available.")
    print(json.dumps(result, indent=2, default=str))
    return 0


def cmd_nodes(args: argparse.Namespace) -> int:
    graph = _graph(args)
    nodes = graph.nodes()
    if args.kind:
        nodes = [n for n in nodes if n.kind == args.kind]
    nodes.sort(key=lambda n: (n.kind, n.id))
    print(json.dumps({"total": len(nodes), "nodes": [n.to_dict() for n in nodes[: args.limit]]}, indent=2))
    return 0


def cmd_impact(args: argparse.Namespace) -> int:
    engine = get_engine()
    result = engine.impact(args.node_id)
    if not result.get("available", True):
        raise SystemExit("Graph not available.")
    if not result.get("found", True):
        raise SystemExit(f"Node '{args.node_id}' not found.")
    print(json.dumps(result, indent=2, default=str))
    return 0


# --------------------------------------------------------------- exports/reports
def cmd_export(args: argparse.Namespace) -> int:
    graph = _graph(args)
    fmt = args.fmt
    from modules.architecture_graph.exports import (
        reactflow,
        cytoscape,
        graphviz,
        mermaid,
        svg,
        html,
    )

    renderers: dict[str, Any] = {
        "reactflow": lambda: json.dumps(reactflow.to_reactflow(graph), indent=2),
        "cytoscape": lambda: json.dumps(cytoscape.to_cytoscape(graph), indent=2),
        "graphviz": lambda: graphviz.to_dot(graph),
        "mermaid": lambda: mermaid.to_mermaid(graph),
        "svg": lambda: svg.to_svg(graph),
        "html": lambda: html.to_html(graph),
    }
    if fmt not in renderers:
        raise SystemExit(f"Unsupported export format: {fmt}. Use one of {sorted(renderers)}.")
    content = renderers[fmt]()
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(content)
        print(f"Exported to {args.out}")
    else:
        sys.stdout.write(content)
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    graph = _graph(args)
    kind = args.kind
    from modules.architecture_graph.reports.architecture_report import ArchitectureReport
    from modules.architecture_graph.reports.dependency_report import DependencyReport
    from modules.architecture_graph.reports.documentation_generator import (
        DocumentationGenerator,
    )

    if kind == "architecture":
        content = json.dumps(ArchitectureReport().to_dict(graph), indent=2, default=str)
    elif kind == "dependency":
        content = json.dumps(DependencyReport().to_dict(graph), indent=2, default=str)
    elif kind == "documentation":
        content = DocumentationGenerator().generate(graph)
    elif kind == "html":
        from modules.architecture_graph.reports.html_report import to_html_report

        content = to_html_report(graph)
    else:
        raise SystemExit(f"Unsupported report kind: {kind}")
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(content)
        print(f"Report written to {args.out}")
    else:
        sys.stdout.write(content if content.endswith("\n") else content + "\n")
    return 0


# ------------------------------------------------------------------------ serve
def cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    from modules.architecture_graph.api.router import api_router

    uvicorn.run(api_router, host=args.host, port=args.port, log_level="info")
    return 0


# ------------------------------------------------------------------------- main
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="architecture-graph", description="Architecture Graph CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("build", help="Full scan + build + persist")
    p.add_argument("--no-persist", action="store_true", help="Skip storage persistence")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("refresh", help="Incremental refresh")
    p.set_defaults(func=cmd_refresh)

    p = sub.add_parser("analyze", help="Full analysis report")
    p.add_argument("--no-build", action="store_true", help="Do not build when missing")
    p.set_defaults(func=cmd_analyze)

    p = sub.add_parser("nodes", help="List nodes")
    p.add_argument("--kind", default=None)
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--no-build", action="store_true", help="Do not build when missing")
    p.set_defaults(func=cmd_nodes)

    p = sub.add_parser("impact", help="Blast-radius analysis")
    p.add_argument("node_id")
    p.add_argument("--no-build", action="store_true", help="Do not build when missing")
    p.set_defaults(func=cmd_impact)

    p = sub.add_parser("export", help="Export the graph")
    p.add_argument("fmt", choices=["reactflow", "cytoscape", "graphviz", "mermaid", "svg", "html"])
    p.add_argument("--out", default=None)
    p.add_argument("--no-build", action="store_true", help="Do not build when missing")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("report", help="Generate a report")
    p.add_argument("kind", choices=["architecture", "dependency", "documentation", "html"])
    p.add_argument("--out", default=None)
    p.add_argument("--no-build", action="store_true", help="Do not build when missing")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("serve", help="Serve the module API")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.set_defaults(func=cmd_serve)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        return int(args.func(args) or 0)
    except SystemExit as exc:
        return int(exc.code or 0)
    except Exception as exc:  # defensive: never crash with a traceback
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
