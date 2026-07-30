from __future__ import annotations

import uuid
from typing import Any

from ...base.base_tool import BaseTool


class TerminalSession(BaseTool):
    _name = "terminal_session"
    _description = "Manage persistent terminal sessions"
    _permissions = ["execute"]

    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "action" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "create")
        session_id = params.get("session_id", "")
        try:
            if action == "create":
                sid = str(uuid.uuid4())
                self._sessions[sid] = {"id": sid, "created": 0, "commands": 0}
                return {"success": True, "session_id": sid}
            elif action == "delete":
                if session_id in self._sessions:
                    del self._sessions[session_id]
                    return {"success": True, "deleted": session_id}
                return {"success": False, "error": "Session not found"}
            elif action == "list":
                return {"success": True, "sessions": list(self._sessions.keys())}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        self._sessions.clear()
