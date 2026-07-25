import os
from pathlib import Path

import typer
from typing_extensions import Annotated


def init(
    name: Annotated[str, typer.Argument(help="Project name")] = "my-superdev-project",
    template: Annotated[str, typer.Option("--template", "-t", help="Project template")] = "default",
    path: Annotated[str, typer.Option("--path", "-p", help="Output path")] = ".",
):
    project_path = Path(path) / name
    if project_path.exists():
        typer.echo(f"Error: Directory {project_path} already exists")
        raise typer.Exit(1)

    typer.echo(f"Creating SuperDev project: {name}")
    typer.echo(f"Template: {template}")
    typer.echo(f"Path: {project_path}")

    dirs = [
        "src",
        "tests",
        "docs",
        "scripts",
        "docker",
        "config",
    ]
    for d in dirs:
        (project_path / d).mkdir(parents=True, exist_ok=True)
        (project_path / d / ".gitkeep").touch()

    (project_path / "README.md").write_text(f"# {name}\n\nSuperDev project created from template: {template}\n")
    (project_path / ".env.example").write_text("# Environment variables\nDATABASE_URL=\nSECRET_KEY=\n")
    (project_path / ".gitignore").write_text("__pycache__/\n.env\n*.pyc\nnode_modules/\n.next/\n")

    typer.echo("Project created successfully!")
    typer.echo(f"\nNext steps:\n  cd {name}\n  superdev doctor\n  superdev init\n")