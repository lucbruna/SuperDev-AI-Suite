"""Canonical CLI entry point.

Usage: python -m modules.ai_evolution_engine.cli <subcommand>
"""
from __future__ import annotations

from modules.ai_evolution_engine.cli.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
