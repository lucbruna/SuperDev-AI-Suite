"""Tool security and permission management."""

from __future__ import annotations

from typing import Any


class ToolSecurity:
    """Enforces security policies for tool usage."""

    def __init__(self) -> None:
        self._denied_tools: set[str] = set()
        self._audit_log: list[dict[str, Any]] = []

    def check(self, tool_id: str, args: dict[str, Any]) -> bool:
        if tool_id in self._denied_tools:
            self._audit_log.append(
                {
                    "tool_id": tool_id,
                    "action": "denied",
                    "reason": "Tool is in deny list",
                }
            )
            return False
        self._audit_log.append(
            {
                "tool_id": tool_id,
                "action": "allowed",
                "args_count": len(args),
            }
        )
        return True

    def deny_tool(self, tool_id: str) -> None:
        self._denied_tools.add(tool_id)

    def allow_tool(self, tool_id: str) -> None:
        self._denied_tools.discard(tool_id)

    def get_audit_log(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._audit_log[-limit:]

    def get_denied(self) -> list[str]:
        return list(self._denied_tools)
