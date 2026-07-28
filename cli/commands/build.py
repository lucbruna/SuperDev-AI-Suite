import asyncio
from pathlib import Path

import typer
from typing_extensions import Annotated

from cli.client import APIClient


async def _build_project(path: Path, output: str | None, client: APIClient) -> dict:
    return await client.post("/api/v1/projects/build", json={"path": str(path), "output": output or "dist"})


def build(
    path: Annotated[str, typer.Argument(help="Project path")] = ".",
    output: Annotated[str | None, typer.Option("--output", "-o", help="Output directory")] = None,
    clean: Annotated[bool, typer.Option("--clean", "-c", help="Clean build")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose output")] = False,
):
    project_path = Path(path).resolve()
    if not project_path.exists():
        typer.echo(f"Error: Path {project_path} does not exist")
        raise typer.Exit(1)

    typer.echo(f"Building project: {project_path}")
    typer.echo(f"Clean build: {clean}")
    typer.echo(f"Output: {output or 'dist'}")

    client = APIClient()
    try:
        result = asyncio.run(_build_project(project_path, output, client))
        if result.get("success"):
            typer.echo("Build completed successfully")
            if verbose and result.get("artifacts"):
                for artifact in result["artifacts"]:
                    typer.echo(f"  - {artifact}")
        else:
            typer.echo(f"Build failed: {result.get('error', 'unknown')}")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)
    finally:
        asyncio.run(client.close())