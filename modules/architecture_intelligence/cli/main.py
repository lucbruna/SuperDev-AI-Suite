"""CLI for architecture intelligence (mirrors architecture_graph.cli)."""
from __future__ import annotations

import argparse
import json
from typing import Any

from modules.architecture_intelligence.core.engine import get_intelligence


def _print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, default=str))


def cmd_status(args: argparse.Namespace) -> int:
    engine = get_intelligence()
    graph = engine.graph(build_if_missing=False)
    _print(
        {
            "module": "architecture_intelligence",
            "version": "1.0.0",
            "available": engine.available,
            "graph_nodes": graph.stats().get("nodes", 0) if graph is not None else 0,
        }
    )
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    _print(get_intelligence().analyze())
    return 0


def cmd_insights(args: argparse.Namespace) -> int:
    _print(get_intelligence().insights(limit=args.limit))
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    _print(get_intelligence().plan())
    return 0


def cmd_optimize(args: argparse.Namespace) -> int:
    _print(get_intelligence().optimize())
    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    if not args.question:
        print("error: --question is required")
        return 1
    _print(get_intelligence().ask(args.question))
    return 0


def cmd_diagnose(args: argparse.Namespace) -> int:
    _print(get_intelligence().diagnose())
    return 0


def cmd_agents(args: argparse.Namespace) -> int:
    _print(get_intelligence().agents())
    return 0


def cmd_snapshot(args: argparse.Namespace) -> int:
    _print(get_intelligence().snapshot())
    return 0


def cmd_history(args: argparse.Namespace) -> int:
    _print(get_intelligence().history_recent(limit=args.limit))
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    _print(get_intelligence().report())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="superdev-intelligence", description="Architecture intelligence CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Module status")
    p = sub.add_parser("analyze", help="Full analysis")
    p = sub.add_parser("insights", help="List insights")
    p.add_argument("--limit", type=int, default=None)
    sub.add_parser("plan", help="Generate roadmap")
    sub.add_parser("optimize", help="Optimization recommendations")
    p = sub.add_parser("ask", help="Ask a question about the architecture")
    p.add_argument("--question", type=str, default="")
    sub.add_parser("diagnose", help="Health diagnostics")
    sub.add_parser("agents", help="Run intelligence agents")
    sub.add_parser("snapshot", help="Capture a metric snapshot")
    p = sub.add_parser("history", help="Recent history snapshots")
    p.add_argument("--limit", type=int, default=20)
    sub.add_parser("report", help="Aggregate dashboard report")

    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0

    handler = {
        "status": cmd_status,
        "analyze": cmd_analyze,
        "insights": cmd_insights,
        "plan": cmd_plan,
        "optimize": cmd_optimize,
        "ask": cmd_ask,
        "diagnose": cmd_diagnose,
        "agents": cmd_agents,
        "snapshot": cmd_snapshot,
        "history": cmd_history,
        "report": cmd_report,
    }.get(args.command)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
