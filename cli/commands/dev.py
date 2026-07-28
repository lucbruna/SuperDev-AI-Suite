from __future__ import annotations

import asyncio

import typer
from typing_extensions import Annotated

from cli.client import APIClient


def dev(
    watch: Annotated[bool, typer.Option("--watch", "-w", help="Watch mode")] = False,
    port: Annotated[int, typer.Option("--port", "-p", help="Port")] = 3000,
):
    client = APIClient()
    try:
        if watch:
            typer.echo(f"Starting dev server on port {port} with hot reload...")
        else:
            typer.echo(f"Starting dev server on port {port}...")
    finally:
        asyncio.run(client.close())