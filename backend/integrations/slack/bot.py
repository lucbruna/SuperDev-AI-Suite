from __future__ import annotations

import os
from typing import Any, Callable

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/integrations/slack", tags=["slack"])
_command_handlers: dict[str, Callable] = {}


def on_command(command: str):
    def decorator(f: Callable):
        _command_handlers[command] = f
        return f
    return decorator


SLACK_VERIFICATION_TOKEN = os.getenv("SLACK_VERIFICATION_TOKEN", "")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")


def _verify_request(body: dict[str, Any]) -> bool:
    if SLACK_VERIFICATION_TOKEN:
        return body.get("token") == SLACK_VERIFICATION_TOKEN
    return True


@router.post("/events")
async def handle_event(request: Request):
    body = await request.json()

    if body.get("type") == "url_verification":
        return {"challenge": body.get("challenge")}

    if not _verify_request(body):
        raise HTTPException(status_code=401, detail="Invalid verification token")

    event = body.get("event", {})
    event_type = event.get("type")

    if event_type == "app_mention":
        text = event.get("text", "").lower()
        for cmd, handler in _command_handlers.items():
            if cmd in text:
                result = await handler(event)
                return {"status": "handled", "command": cmd, "result": result}
        return {"status": "unrecognized", "text": text}

    if event_type == "message" and event.get("channel_type") == "im":
        text = event.get("text", "").lower()
        for cmd, handler in _command_handlers.items():
            if cmd in text:
                result = await handler(event)
                return {"status": "handled", "command": cmd, "result": result}
        return {"status": "echo", "text": text}

    return {"status": "ignored", "event_type": event_type}


@router.get("/commands")
async def list_commands() -> dict[str, list[str]]:
    return {"commands": list(_command_handlers.keys())}


@on_command("deploy")
async def _handle_deploy(event: dict[str, Any]) -> dict[str, Any]:
    return {"action": "deploy", "status": "started", "message": "Deployment initiated"}


@on_command("status")
async def _handle_status(event: dict[str, Any]) -> dict[str, Any]:
    return {"action": "status", "agents": 3, "active": 2, "completed": 15}


@on_command("agents")
async def _handle_list_agents(event: dict[str, Any]) -> dict[str, Any]:
    return {"action": "list_agents", "agents": ["Architect", "Executor", "Reviewer", "Deployer"]}


@on_command("help")
async def _handle_help(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "action": "help",
        "commands": [
            {"command": "deploy [env]", "description": "Deploy to environment"},
            {"command": "status", "description": "Check system status"},
            {"command": "agents", "description": "List active agents"},
            {"command": "run [workflow]", "description": "Execute a workflow"},
            {"command": "help", "description": "Show this help"},
        ],
    }


@on_command("run")
async def _handle_run(event: dict[str, Any]) -> dict[str, Any]:
    text = event.get("text", "").lower()
    workflow = text.replace("run", "").strip()
    return {"action": "run_workflow", "workflow": workflow or "default", "status": "queued"}


@router.post("/send")
async def send_message(channel: str, text: str) -> dict[str, Any]:
    return {"channel": channel, "text": text, "status": "sent"}