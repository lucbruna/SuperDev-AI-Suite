from __future__ import annotations

import json

from agents.debugger.studio import AgentStudioBackend
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from backend.websocket.events import EventType, WSEvent
from backend.websocket.manager import manager

router = APIRouter(prefix="/studio")
_backend = AgentStudioBackend()


@router.websocket("/ws")
async def studio_websocket(websocket: WebSocket, session_id: str = "default"):
    channel = f"studio:{session_id}"
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type", "")

            if msg_type == "ping":
                await manager.send_personal({"type": "pong"}, websocket)

            elif msg_type == "session:create":
                project_id = message.get("project_id", "default")
                sid = await _backend.create_session(project_id)
                await manager.send_personal({"type": "session:created", "session_id": sid}, websocket)

            elif msg_type == "session:stop":
                sid = message.get("session_id")
                await _backend.stop_session(sid)
                await manager.send_personal({"type": "session:stopped", "session_id": sid}, websocket)

            elif msg_type == "step:over":
                sid = message.get("session_id")
                _backend._sessions.get(sid, {}).pop("_paused", None)
                await _broadcast_event(session_id, "STUDIO_STEP_COMPLETE", {"session_id": sid, "action": "step_over"})

            elif msg_type == "step:into":
                sid = message.get("session_id")
                _backend.set_step_mode(sid, True)
                await _broadcast_event(session_id, "STUDIO_STEP_COMPLETE", {"session_id": sid, "action": "step_into"})

            elif msg_type == "step:out":
                sid = message.get("session_id")
                _backend.set_step_mode(sid, False)
                await _broadcast_event(session_id, "STUDIO_STEP_COMPLETE", {"session_id": sid, "action": "step_out"})

            elif msg_type == "resume":
                sid = message.get("session_id")
                _backend.resume_session(sid)
                await _broadcast_event(session_id, "STUDIO_STATE_TRANSITION", {"session_id": sid, "status": "running"})

            elif msg_type == "breakpoint:set":
                sid = message.get("session_id")
                node_id = message.get("node_id")
                bp = _backend.set_breakpoint(sid, node_id)
                await manager.send_personal(
                    {"type": "breakpoint:set", "breakpoint": bp.to_dict() if bp else None}, websocket
                )

            elif msg_type == "breakpoint:remove":
                sid = message.get("session_id")
                bp_id = message.get("breakpoint_id")
                _backend.remove_breakpoint(sid, bp_id)
                await manager.send_personal({"type": "breakpoint:removed", "breakpoint_id": bp_id}, websocket)

            elif msg_type == "get:state":
                sid = message.get("session_id")
                state = _backend.get_graph_state(sid)
                variables = _backend.get_variables(sid)
                events = _backend.get_event_history(sid)
                breakpoints = _backend.list_breakpoints(sid)
                await manager.send_personal(
                    {
                        "type": "state:snapshot",
                        "session_id": sid,
                        "graph": state,
                        "variables": variables,
                        "events": [e.to_dict() if hasattr(e, "to_dict") else e for e in events[-50:]],
                        "breakpoints": [bp.to_dict() if hasattr(bp, "to_dict") else bp for bp in (breakpoints or [])],
                    },
                    websocket,
                )

    except WebSocketDisconnect:
        await manager.disconnect(websocket, channel)


async def _broadcast_event(session_id: str, event_type: str, payload: dict) -> None:
    event = WSEvent(
        type=EventType[event_type] if event_type in EventType.__members__ else EventType.LOG_MESSAGE,
        payload=payload,
    )
    await manager.broadcast(f"studio:{session_id}", event.to_dict())


@router.post("/sessions")
async def create_session(project_id: str = "default"):
    session_id = await _backend.create_session(project_id)
    return {"session_id": session_id, "status": "created"}


@router.get("/sessions")
async def list_sessions():
    sessions = await _backend.list_sessions()
    return {"sessions": sessions}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    state = _backend.get_graph_state(session_id)
    variables = _backend.get_variables(session_id)
    events = _backend.get_event_history(session_id)
    breakpoints = _backend.list_breakpoints(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session_id,
        "graph": state,
        "variables": variables,
        "events": [e.to_dict() if hasattr(e, "to_dict") else e for e in events[-100:]],
        "breakpoints": [bp.to_dict() if hasattr(bp, "to_dict") else bp for bp in (breakpoints or [])],
    }


@router.delete("/sessions/{session_id}")
async def destroy_session(session_id: str):
    await _backend.destroy_session(session_id)
    return {"session_id": session_id, "status": "destroyed"}


@router.post("/sessions/{session_id}/breakpoints")
async def set_breakpoint(session_id: str, node_id: str):
    bp = _backend.set_breakpoint(session_id, node_id)
    if not bp:
        raise HTTPException(status_code=404, detail="Session or node not found")
    return {"breakpoint": bp.to_dict() if hasattr(bp, "to_dict") else bp}


@router.delete("/sessions/{session_id}/breakpoints/{breakpoint_id}")
async def remove_breakpoint(session_id: str, breakpoint_id: str):
    _backend.remove_breakpoint(session_id, breakpoint_id)
    return {"status": "removed"}


@router.post("/sessions/{session_id}/resume")
async def resume_session(session_id: str):
    _backend.resume_session(session_id)
    return {"status": "resumed"}


@router.post("/sessions/{session_id}/step")
async def step_session(session_id: str, mode: str = "over"):
    _backend.set_step_mode(session_id, True)
    _backend._sessions.get(session_id, {}).pop("_paused", None)
    return {"status": "stepping", "mode": mode}
