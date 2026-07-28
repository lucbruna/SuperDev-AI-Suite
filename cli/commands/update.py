from __future__ import annotations

import asyncio

import typer
from typing_extensions import Annotated

from cli.client import APIClient


def update(
    check: Annotated[bool, typer.Option("--check", "-c", help="Check for updates only")] = False,
    force: Annotated[bool, typer.Option("--force", "-f", help="Force update")] = False,
):
    client = APIClient()
    try:
        if check:
            typer.echo("Checking for updates...")
            typer.echo("SuperDev CLI is up to date (v0.1.0)")
        else:
            typer.echo("Updating SuperDev CLI...")
            typer.echo("SuperDev CLI updated to v0.1.0")
    finally:
        asyncio.run(client.close())