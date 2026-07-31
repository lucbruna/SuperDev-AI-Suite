"""Tool registration and lifecycle management."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class ToolRegistry:
    """Manages the registration and lifecycle of agent tools."""

    def __init__(self) -> None:
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        tool_id = tool.get("id", f"tool_{len(self._tools) + 1}")
        self._tools[tool_id] = {
            "id": tool_id,
            "name": tool.get("name", "Unnamed Tool"),
            "description": tool.get("description", ""),
            "category": tool.get("category", "general"),
            "version": tool.get("version", "1.0.0"),
            "parameters": tool.get("parameters", {}),
            "enabled": True,
        }
        return {"status": "registered", "tool_id": tool_id}

    def get(self, tool_id: str) -> Optional[Dict[str, Any]]:
        return dict(self._tools.get(tool_id)) if tool_id in self._tools else None

    def remove(self, tool_id: str) -> bool:
        if tool_id in self._tools:
            del self._tools[tool_id]
            return True
        return False

    def enable(self, tool_id: str) -> bool:
        if tool_id in self._tools:
            self._tools[tool_id]["enabled"] = True
            return True
        return False

    def disable(self, tool_id: str) -> bool:
        if tool_id in self._tools:
            self._tools[tool_id]["enabled"] = False
            return True
        return False

    def list_all(self) -> List[Dict[str, Any]]:
        return [
            {"id": t["id"], "name": t["name"], "category": t["category"]}
            for t in self._tools.values()
        ]

    def count(self) -> int:
        return len(self._tools)
