"""Tool execution handler."""
from __future__ import annotations

import time
from typing import Any, Dict


class ToolExecutor:
    """Executes registered tools with given arguments."""

    def __init__(self) -> None:
        self._history: list[Dict[str, Any]] = []

    def execute(self, tool: Dict[str, Any], args: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        result = {
            "tool_id": tool.get("id", "unknown"),
            "tool_name": tool.get("name", "unknown"),
            "args": args,
            "status": "completed",
            "output": f"Tool {tool.get('name', '?')} executed with {len(args)} arguments",
            "timestamp": time.time(),
            "duration_ms": round((time.time() - start) * 1000, 2),
        }
        self._history.append(result)
        return result

    def get_history(self, limit: int = 20) -> list[Dict[str, Any]]:
        return self._history[-limit:]
