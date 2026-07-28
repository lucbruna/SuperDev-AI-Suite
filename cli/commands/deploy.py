import asyncio
from pathlib import Path

import typer
from typing_extensions import Annotated

from cli.client import APIClient


async def _deploy_project(
    path: str,
    target: str,
    version: str | None,
    client: APIClient,
) -> dict:
    return await client.post(
        "/api/v1/projects/deploy",
        json={"path": path, "target": target, "version": version or "latest"},
    )


def deploy(
    path: Annotated[str, typer.Argument(help="Project path or name")] = ".",
    target: Annotated[str, typer.Option("--target", "-t", help="Deployment target (staging/production)")] = "staging",
    version: Annotated[str | None, typer.Option("--version", "-v", help="Version tag")] = None,
    wait: Annotated[bool, typer.Option("--wait", "-w", help="Wait for deployment")] = False,
):
    project_path = Path(path).resolve()
    typer.echo(f"Deploying {project_path} to {target}")

    client = APIClient()
    try:
        result = asyncio.run(_deploy_project(str(project_path), target, version, client))
        if result.get("success"):
            typer.echo(f"Deploy to {target} completed")
            if result.get("url"):
                typer.echo(f"URL: {result['url']}")
        else:
            typer.echo(f"Deploy failed: {result.get('error', 'unknown')}")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)
    finally:
        asyncio.run(client.close())