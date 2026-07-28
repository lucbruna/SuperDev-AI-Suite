from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/collab", tags=["collaboration"])

_sessions: dict[str, dict[str, Any]] = {}
_connections: dict[str, list[WebSocket]] = {}
_operations: dict[str, list[dict[str, Any]]] = {}


class OTDoc:
    def __init__(self, content: str = ""):
        self.content = content
        self.revision = 0

    def apply_op(self, op: dict[str, Any]) -> dict[str, Any]:
        kind = op.get("kind")
        pos = op.get("position", 0)
        if kind == "insert":
            self.content = self.content[:pos] + op["text"] + self.content[pos:]
        elif kind == "delete":
            length = op.get("length", 0)
            deleted = self.content[pos : pos + length]
            self.content = self.content[:pos] + self.content[pos + length:]
            op["deleted"] = deleted
        elif kind == "replace":
            length = op.get("length", 0)
            deleted = self.content[pos : pos + length]
            self.content = self.content[:pos] + op["text"] + self.content[pos + length:]
            op["deleted"] = deleted
        self.revision += 1
        return op

    def transform(self, op_a: dict[str, Any], op_b: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        if op_a["kind"] == "insert" and op_b["kind"] == "insert":
            if op_a["position"] < op_b["position"]:
                return (op_a, {**op_b, "position": op_b["position"] + len(op_a["text"])})
            return ({**op_a, "position": op_a["position"] + len(op_b["text"])}, op_b)
        return (op_a, op_b)


_docs: dict[str, OTDoc] = {}


@router.websocket("/ws/{session_id}")
async def collab_ws(ws: WebSocket, session_id: str, user_id: str = "anonymous"):
    await ws.accept()
    if session_id not in _connections:
        _connections[session_id] = []
        _operations[session_id] = []
        _docs[session_id] = OTDoc()
    _connections[session_id].append(ws)

    await ws.send_json({"type": "init", "revision": _docs[session_id].revision, "content": _docs[session_id].content, "users": len(_connections[session_id])})

    try:
        while True:
            data = await ws.receive_json()
            if data.get("type") == "op":
                op = data["op"]
                doc = _docs[session_id]
                op["user_id"] = user_id
                op["id"] = str(uuid.uuid4().hex[:8])
                doc.apply_op(op)
                _operations[session_id].append(op)
                for conn in _connections[session_id]:
                    if conn != ws:
                        try:
                            await conn.send_json({"type": "op", "op": op, "revision": doc.revision})
                        except Exception:
                            pass
            elif data.get("type") == "cursor":
                for conn in _connections[session_id]:
                    if conn != ws:
                        try:
                            await conn.send_json({"type": "cursor", "user_id": user_id, "position": data.get("position", 0)})
                        except Exception:
                            pass
    except WebSocketDisconnect:
        _connections[session_id].remove(ws)
        if not _connections[session_id]:
            del _connections[session_id]
            del _operations[session_id]
            del _docs[session_id]


@router.get("/sessions")
async def list_sessions():
    return {"sessions": [{"id": sid, "users": len(conns), "revision": _docs.get(sid, OTDoc()).revision} for sid, conns in _connections.items()]}


@router.get("/sessions/{session_id}/ops")
async def get_operations(session_id: str):
    return {"operations": _operations.get(session_id, [])}