import asyncio
import json

import typer
from typing_extensions import Annotated

from cli.client import APIClient


async def _list_workflows(client: APIClient) -> dict:
    return await client.get("/api/v1/workflows")


async def _get_workflow(workflow_id: str, client: APIClient) -> dict:
    return await client.get(f"/api/v1/workflows/{workflow_id}")


async def _create_workflow(name: str, definition: dict, client: APIClient) -> dict:
    return await client.post("/api/v1/workflows", json={"name": name, "definition": definition})


async def _delete_workflow(workflow_id: str, client: APIClient) -> dict:
    return await client.delete(f"/api/v1/workflows/{workflow_id}")


def workflow(
    action: Annotated[str, typer.Argument(help="Action: list, get, create, delete, run")],
    workflow_id: Annotated[str | None, typer.Argument(help="Workflow ID")] = None,
    name: Annotated[str | None, typer.Option("--name", "-n", help="Workflow name")] = None,
    definition: Annotated[str | None, typer.Option("--definition", "-d", help="Path to workflow YAML/JSON")] = None,
    json_output: Annotated[bool, typer.Option("--json", "-j", help="JSON output")] = False,
):
    client = APIClient()
    try:
        if action == "list":
            result = asyncio.run(_list_workflows(client))
            items = result.get("workflows", result.get("items", []))
            if json_output:
                typer.echo(json.dumps(items, indent=2, default=str))
            else:
                if not items:
                    typer.echo("No workflows found")
                else:
                    for w in items:
                        typer.echo(f"  {w.get('id', '?')[:8]}  {w.get('name', '?')}  [{w.get('status', '?')}]")
        elif action == "get":
            if not workflow_id:
                typer.echo("Error: workflow_id required for 'get' action")
                raise typer.Exit(1)
            result = asyncio.run(_get_workflow(workflow_id, client))
            typer.echo(json.dumps(result, indent=2, default=str))
        elif action == "create":
            if not name:
                typer.echo("Error: --name required for 'create' action")
                raise typer.Exit(1)
            def_data = {}
            if definition:
                from pathlib import Path
                import yaml
                def_path = Path(definition)
                if not def_path.exists():
                    typer.echo(f"Error: Definition file {definition} not found")
                    raise typer.Exit(1)
                content = def_path.read_text()
                def_data = yaml.safe_load(content) or {}
            result = asyncio.run(_create_workflow(name, def_data, client))
            typer.echo(f"Workflow created: {result.get('id', '?')}")
        elif action == "delete":
            if not workflow_id:
                typer.echo("Error: workflow_id required for 'delete' action")
                raise typer.Exit(1)
            asyncio.run(_delete_workflow(workflow_id, client))
            typer.echo(f"Workflow {workflow_id} deleted")
        elif action == "run":
            if not workflow_id:
                typer.echo("Error: workflow_id required for 'run' action. Use `superdev run` instead.")
                raise typer.Exit(1)
            from cli.commands.run import run as run_cmd
            run_cmd(workflow_id)
        else:
            typer.echo(f"Unknown action: {action} (use: list, get, create, delete, run)")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)
    finally:
        asyncio.run(client.close())