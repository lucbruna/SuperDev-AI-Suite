import asyncio
import json

import typer
from typing_extensions import Annotated

from cli.client import APIClient


async def _run_eval(
    prompt: str,
    model_a: str,
    model_b: str,
    client: APIClient,
) -> dict:
    return await client.post(
        "/api/v1/evals/compare",
        json={"prompt": prompt, "model_a": model_a, "model_b": model_b},
    )


def eval(
    prompt: Annotated[str, typer.Argument(help="Prompt or task to evaluate")],
    model_a: Annotated[str, typer.Option("--model-a", "-a", help="First model")] = "gpt-4",
    model_b: Annotated[str, typer.Option("--model-b", "-b", help="Second model")] = "claude-3",
    output: Annotated[str | None, typer.Option("--output", "-o", help="Save results to file")] = None,
):
    typer.echo(f"Evaluating prompt against {model_a} vs {model_b}")
    typer.echo(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

    client = APIClient()
    try:
        result = asyncio.run(_run_eval(prompt, model_a, model_b, client))
        typer.echo(json.dumps(result, indent=2, default=str))

        if output:
            output_path = typer.Path(output)
            with open(str(output_path), "w") as f:
                json.dump(result, f, indent=2, default=str)
            typer.echo(f"Results saved to {output}")
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)
    finally:
        asyncio.run(client.close())