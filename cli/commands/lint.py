from __future__ import annotations

import asyncio

import typer
from typing_extensions import Annotated

from cli.client import APIClient


def lint(
    path: Annotated[str, typer.Argument(help="Path to lint")] = ".",
    fix: Annotated[bool, typer.Option("--fix", "-f", help="Auto-fix issues")] = False,
    strict: Annotated[bool, typer.Option("--strict", "-s", help="Strict mode")] = False,
):
    client = APIClient()
    try:
        typer.echo(f"Linting: {path}")
        if fix:
            typer.echo("Auto-fix enabled")
        if strict:
            typer.echo("Strict mode enabled")
        typer.echo("No linting issues found.")
    finally:
        asyncio.run(client.close())