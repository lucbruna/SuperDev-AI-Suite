"""CLI entry point for the AI Evolution Engine (stdlib argparse only)."""
from __future__ import annotations

import argparse
import json

from modules.ai_evolution_engine.api.evolution_api import EvolutionAPI
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.core.evolution_manager import EvolutionManager
from modules.ai_evolution_engine.integrations import build_default_registry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-evolution",
        description="AI Evolution Engine - deterministic evolution analysis.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="Show engine state.")
    sub.add_parser("analyze", help="Run a full analysis cycle.")
    sub.add_parser("recommend", help="Generate recommendations.")
    sub.add_parser("integrations", help="List integration availability.")
    approve = sub.add_parser("approve", help="Approve a recommendation.")
    approve.add_argument("recommendation_id")
    reject = sub.add_parser("reject", help="Reject a recommendation.")
    reject.add_argument("recommendation_id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manager = EvolutionManager(EvolutionContext())
    api = EvolutionAPI(manager)
    if args.command in ("status", "analyze", "recommend"):
        result = api.handle(args.command)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if args.command in ("approve", "reject"):
        result = api.handle(args.command, {"recommendation_id": args.recommendation_id})
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if args.command == "integrations":
        registry = build_default_registry()
        print(json.dumps(registry.summary(), indent=2, sort_keys=True))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
