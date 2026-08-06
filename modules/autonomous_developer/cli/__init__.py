"""CLI: deterministic argument parsing and command dispatch."""
from __future__ import annotations

from modules.autonomous_developer.cli.parser import (
    DEFAULT_COMMANDS,
    ArgumentParser,
    CLI,
    CLIArgs,
    CLIError,
    CLIResult,
)

__all__ = [
    "DEFAULT_COMMANDS",
    "ArgumentParser",
    "CLI",
    "CLIArgs",
    "CLIError",
    "CLIResult",
]
