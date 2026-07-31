from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Request

router = APIRouter(prefix="/integrations/teams", tags=["teams"])
_command_handlers: dict[str, Callable] = {}

TEAMS_APP_ID = os.getenv("TEAMS_APP_ID", "")


def on_command(command: str):
    def decorator(f: Callable):
        _command_handlers[command] = f
        return f
    return decorator


@router.post("/messages")
async def handle_message(request: Request):
    body = await request.json()
    text = body.get("text", "").lower()
    for cmd, handler in _command_handlers.items():
        if cmd in text:
            result = await handler(body)
            return {"status": "handled", "command": cmd, "result": result}
    return {"status": "unrecognized", "text": text}


@router.post("/adaptive-card")
async def send_adaptive_card(payload: dict[str, Any]) -> dict[str, Any]:
    return {"status": "sent", "card_type": "adaptive", "conversation_id": payload.get("conversation_id")}


@on_command("deploy")
async def _handle_deploy(event: dict[str, Any]) -> dict[str, Any]:
    return {"action": "deploy", "status": "started"}


@on_command("status")
async def _handle_status(event: dict[str, Any]) -> dict[str, Any]:
    return {"action": "status", "system": "healthy", "agents": 4, "uptime": "99.9%"}


@on_command("help")
async def _handle_help(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "action": "help",
        "commands": [
            {"command": "deploy [env]", "description": "Deploy to environment"},
            {"command": "status", "description": "Check system health"},
            {"command": "agents", "description": "List active agents"},
            {"command": "help", "description": "Show commands"},
        ],
    }


@on_command("agents")
async def _handle_agents(event: dict[str, Any]) -> dict[str, Any]:
    return {"action": "list_agents", "agents": ["Planner", "Coder", "Reviewer"]}
