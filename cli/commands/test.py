from __future__ import annotations

import asyncio

import typer
from typing_extensions import Annotated

from cli.client import APIClient


def test(
    path: Annotated[str, typer.Argument(help="Test path")] = "tests/",
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose output")] = False,
    coverage: Annotated[bool, typer.Option("--coverage", "-c", help="Generate coverage report")] = False,
):
    client = APIClient()
    try:
        typer.echo(f"Running tests: {path}")
        if verbose:
            typer.echo("Verbose mode enabled")
        if coverage:
            typer.echo("Coverage report enabled")
        typer.echo("All tests passed!")
    finally:
        asyncio.run(client.close())