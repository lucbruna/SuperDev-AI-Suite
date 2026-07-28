import asyncio

import typer
from typing_extensions import Annotated

from cli.client import APIClient
from cli.commands.agent import agent
from cli.commands.build import build
from cli.commands.deploy import deploy
from cli.commands.dev import dev
from cli.commands.doctor import doctor
from cli.commands.eval import eval
from cli.commands.init import init
from cli.commands.lint import lint
from cli.commands.run import run
from cli.commands.test import test
from cli.commands.update import update
from cli.commands.workflow import workflow
from cli.completion import completion

app = typer.Typer(name="superdev")

app.command(name="init")(init)
app.command(name="doctor")(doctor)
app.command(name="run")(run)
app.command(name="build")(build)
app.command(name="deploy")(deploy)
app.command(name="dev")(dev)
app.command(name="test")(test)
app.command(name="lint")(lint)
app.command(name="update")(update)
app.command(name="eval")(eval)
app.command(name="agent")(agent)
app.command(name="workflow")(workflow)
app.command(name="completion")(completion)


@app.callback()
def callback():
    pass


@app.command()
def login(
    email: Annotated[str, typer.Option("--email", "-e", help="Email")],
    password: Annotated[str, typer.Option("--password", "-p", prompt=True, hide_input=True, help="Password")],
):
    client = APIClient()
    try:
        result = asyncio.run(client.login(email, password))
        typer.echo(f"Logged in as {result.get('email', email)}")
    except Exception as e:
        typer.echo(f"Login failed: {e}")
        raise typer.Exit(1)
    finally:
        asyncio.run(client.close())


@app.command()
def logout():
    client = APIClient()
    try:
        asyncio.run(client.logout())
        typer.echo("Logged out")
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)
    finally:
        asyncio.run(client.close())


@app.command()
def status():
    client = APIClient()
    try:
        result = asyncio.run(client.get("/api/v1/health"))
        typer.echo(f"SuperDev API: {'UP' if result.get('status') == 'ok' else 'DOWN'}")
        if result.get("version"):
            typer.echo(f"Version: {result['version']}")
        typer.echo(f"Environment: {client.config.environment}")
        typer.echo(f"API URL: {client.config.api_url}")
    except Exception as e:
        typer.echo(f"Status check failed: {e}")
        typer.echo("Is the SuperDev server running?")
        raise typer.Exit(1)
    finally:
        asyncio.run(client.close())


@app.command()
def version():
    typer.echo("SuperDev CLI v0.1.0")


def cli():
    app()