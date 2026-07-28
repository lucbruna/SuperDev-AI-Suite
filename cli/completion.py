import shutil
from pathlib import Path

import typer
from typing_extensions import Annotated


def _get_completion_dir() -> Path:
    home = Path.home()
    if shutil.which("zsh"):
        zsh_completion = home / ".zsh" / "completions"
        zsh_completion.mkdir(parents=True, exist_ok=True)
        return zsh_completion
    if shutil.which("bash"):
        bash_completion = home / ".bash_completion.d"
        bash_completion.mkdir(parents=True, exist_ok=True)
        return bash_completion
    return home / ".superdev" / "completions"


def completion(
    shell: Annotated[str, typer.Argument(help="Shell type: bash, zsh, fish, powershell")] = "auto",
    install: Annotated[bool, typer.Option("--install", "-i", help="Install completion permanently")] = False,
):
    shell_map = {
        "bash": "bash.sh",
        "zsh": "zsh.sh",
        "fish": "fish.sh",
        "powershell": "powershell.ps1",
    }

    if shell == "auto":
        if shutil.which("zsh"):
            shell = "zsh"
        elif shutil.which("bash"):
            shell = "bash"
        elif shutil.which("fish"):
            shell = "fish"
        else:
            shell = "bash"

    script_name = shell_map.get(shell)
    if not script_name:
        typer.echo(f"Unsupported shell: {shell} (use: bash, zsh, fish, powershell)")
        raise typer.Exit(1)

    script_path = Path(__file__).parent / "completion" / script_name
    if not script_path.exists():
        typer.echo(f"Completion script not found: {script_path}")
        raise typer.Exit(1)

    content = script_path.read_text()

    if install:
        dest = _get_completion_dir() / f"_superdev.{shell}"
        dest.write_text(content)
        typer.echo(f"Completions installed to {dest}")
        typer.echo(f"Add to your .{shell}rc: source {dest}")
    else:
        typer.echo(content)