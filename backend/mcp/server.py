from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/mcp", tags=["mcp"])


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any] | None = None


class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any]
    session_id: str | None = None


class ToolCallResponse(BaseModel):
    tool_call_id: str
    tool_name: str
    result: Any
    error: str | None = None
    duration_ms: float
    timestamp: str


_internal_registry: dict[str, ToolDefinition] = {}
_session_store: dict[str, dict[str, Any]] = {}


def register_tool(tool: ToolDefinition) -> None:
    _internal_registry[tool.name] = tool


@router.get("/tools")
async def list_tools() -> list[ToolDefinition]:
    return list(_internal_registry.values())


@router.get("/tools/{tool_name}")
async def get_tool(tool_name: str) -> ToolDefinition:
    tool = _internal_registry.get(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    return tool


@router.post("/call")
async def call_tool(req: ToolCallRequest) -> ToolCallResponse:
    import time
    tool = _internal_registry.get(req.tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{req.tool_name}' not found")

    start = time.time()
    tool_call_id = f"mcp_{uuid.uuid4().hex[:12]}"
    try:
        handler = _callable_registry.get(req.tool_name)
        if not handler:
            raise ValueError(f"No handler registered for '{req.tool_name}'")
        result = await handler(req.arguments)
        duration = (time.time() - start) * 1000
        return ToolCallResponse(
            tool_call_id=tool_call_id,
            tool_name=req.tool_name,
            result=result,
            duration_ms=round(duration, 2),
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        duration = (time.time() - start) * 1000
        return ToolCallResponse(
            tool_call_id=tool_call_id,
            tool_name=req.tool_name,
            result=None,
            error=str(e),
            duration_ms=round(duration, 2),
            timestamp=datetime.utcnow().isoformat(),
        )


_callable_registry: dict[str, callable] = {}


def register_handler(tool_name: str, handler: callable) -> None:
    _callable_registry[tool_name] = handler


@router.get("/session/{session_id}")
async def get_session(session_id: str) -> dict[str, Any]:
    session = _session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/session")
async def create_session(context: dict[str, Any] | None = None) -> dict[str, Any]:
    session_id = f"mcp_sess_{uuid.uuid4().hex[:16]}"
    _session_store[session_id] = {
        "session_id": session_id,
        "context": context or {},
        "history": [],
        "created_at": datetime.utcnow().isoformat(),
    }
    return _session_store[session_id]
