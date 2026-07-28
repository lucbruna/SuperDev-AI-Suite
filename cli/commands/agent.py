import asyncio
import json

import typer
from typing_extensions import Annotated

from cli.client import APIClient


async def _list_agents(client: APIClient) -> dict:
    return await client.get("/api/v1/agents")


async def _get_agent(agent_id: str, client: APIClient) -> dict:
    return await client.get(f"/api/v1/agents/{agent_id}")


async def _run_agent(agent_id: str, task: str, client: APIClient) -> dict:
    return await client.post(f"/api/v1/agents/{agent_id}/execute", json={"task": task})


def agent(
    action: Annotated[str, typer.Argument(help="Action: list, get, run")],
    agent_id: Annotated[str | None, typer.Argument(help="Agent ID")] = None,
    task: Annotated[str | None, typer.Option("--task", "-t", help="Task for the agent")] = None,
    json_output: Annotated[bool, typer.Option("--json", "-j", help="JSON output")] = False,
):
    client = APIClient()
    try:
        if action == "list":
            result = asyncio.run(_list_agents(client))
            agents = result.get("agents", result.get("items", []))
            if json_output:
                typer.echo(json.dumps(agents, indent=2, default=str))
            else:
                if not agents:
                    typer.echo("No agents found")
                else:
                    for a in agents:
                        typer.echo(f"  {a.get('id', '?')[:8]}  {a.get('name', '?')}  [{a.get('status', '?')}]")
        elif action == "get":
            if not agent_id:
                typer.echo("Error: agent_id required for 'get' action")
                raise typer.Exit(1)
            result = asyncio.run(_get_agent(agent_id, client))
            typer.echo(json.dumps(result, indent=2, default=str))
        elif action == "run":
            if not agent_id:
                typer.echo("Error: agent_id required for 'run' action")
                raise typer.Exit(1)
            if not task:
                typer.echo("Error: --task required for 'run' action")
                raise typer.Exit(1)
            result = asyncio.run(_run_agent(agent_id, task, client))
            if json_output:
                typer.echo(json.dumps(result, indent=2, default=str))
            else:
                output = result.get("output", result.get("result", ""))
                if result.get("success"):
                    typer.echo(f"Agent completed: {str(output)[:200]}")
                else:
                    typer.echo(f"Agent failed: {result.get('error', 'unknown')}")
                    raise typer.Exit(1)
        else:
            typer.echo(f"Unknown action: {action} (use: list, get, run)")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)
    finally:
        asyncio.run(client.close())