from typing import Any

import typer
from typing_extensions import Annotated

from cli.client import APIClient


async def _run_workflow(
    workflow_id: str,
    params: dict[str, Any],
    wait: bool,
    client: APIClient,
) -> dict[str, Any]:
    result = await client.post(
        f"/api/v1/workflows/{workflow_id}/execute",
        json={"params": params, "wait": wait},
    )
    return result


def run(
    workflow: Annotated[str, typer.Argument(help="Workflow ID or name to run")],
    param: Annotated[list[str] | None, typer.Option("--param", "-p", help="Parameters as key=value")] = None,
    wait: Annotated[bool, typer.Option("--wait", "-w", help="Wait for completion")] = False,
    env: Annotated[str | None, typer.Option("--env", "-e", help="Environment")] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose output")] = False,
    json_output: Annotated[bool, typer.Option("--json", "-j", help="JSON output")] = False,
):
    import asyncio

    params_dict: dict[str, Any] = {}
    if param:
        for p in param:
            if "=" not in p:
                typer.echo(f"Invalid param format: {p} (expected key=value)")
                raise typer.Exit(1)
            key, value = p.split("=", 1)
            params_dict[key] = value

    client = APIClient()
    try:
        result = asyncio.run(_run_workflow(workflow, params_dict, wait, client))
        if json_output:
            import json
            typer.echo(json.dumps(result, indent=2, default=str))
        else:
            typer.echo(f"Workflow {workflow} executed successfully" if result.get("success") else f"Workflow {workflow} failed: {result.get('error', 'unknown')}")
            if verbose and result.get("output"):
                typer.echo(f"Output: {result['output']}")
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)
    finally:
        import asyncio
        asyncio.run(client.close())