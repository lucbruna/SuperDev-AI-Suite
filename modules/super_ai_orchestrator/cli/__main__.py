"""Canonical CLI entry point.

Usage: python -m modules.super_ai_orchestrator.cli <subcommand>
"""
from __future__ import annotations

from modules.super_ai_orchestrator.cli.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
