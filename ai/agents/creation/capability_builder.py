"""Fluent builder for agent capabilities."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class CapabilityBuilder:
    """Fluent builder pattern for assembling agent capabilities."""

    def __init__(self) -> None:
        self._capabilities: List[str] = []
        self._tools: List[Dict[str, Any]] = []
        self._permissions: List[str] = []
        self._constraints: List[str] = []

    def with_chat(self) -> "CapabilityBuilder":
        if "chat" not in self._capabilities:
            self._capabilities.append("chat")
        return self

    def with_stream(self) -> "CapabilityBuilder":
        if "stream" not in self._capabilities:
            self._capabilities.append("stream")
        return self

    def with_vision(self) -> "CapabilityBuilder":
        if "vision" not in self._capabilities:
            self._capabilities.append("vision")
        return self

    def with_tools(self, tool_names: Optional[List[str]] = None) -> "CapabilityBuilder":
        if "tools" not in self._capabilities:
            self._capabilities.append("tools")
        for name in (tool_names or []):
            self._tools.append({"name": name, "enabled": True})
        return self

    def with_code_execution(self) -> "CapabilityBuilder":
        if "code_execution" not in self._capabilities:
            self._capabilities.append("code_execution")
        return self

    def with_memory(self, memory_type: str = "short_term") -> "CapabilityBuilder":
        if "memory" not in self._capabilities:
            self._capabilities.append("memory")
        self._tools.append({"name": f"memory_{memory_type}", "enabled": True})
        return self

    def with_planning(self) -> "CapabilityBuilder":
        if "planning" not in self._capabilities:
            self._capabilities.append("planning")
        return self

    def with_reasoning(self) -> "CapabilityBuilder":
        if "reasoning" not in self._capabilities:
            self._capabilities.append("reasoning")
        return self

    def with_learning(self) -> "CapabilityBuilder":
        if "learning" not in self._capabilities:
            self._capabilities.append("learning")
        return self

    def with_permission(self, permission: str) -> "CapabilityBuilder":
        if permission not in self._permissions:
            self._permissions.append(permission)
        return self

    def with_constraint(self, constraint: str) -> "CapabilityBuilder":
        if constraint not in self._constraints:
            self._constraints.append(constraint)
        return self

    def with_embeddings(self) -> "CapabilityBuilder":
        if "embeddings" not in self._capabilities:
            self._capabilities.append("embeddings")
        return self

    def build(self) -> Dict[str, Any]:
        return {
            "capabilities": list(self._capabilities),
            "tools": list(self._tools),
            "permissions": list(self._permissions),
            "constraints": list(self._constraints),
        }

    def reset(self) -> "CapabilityBuilder":
        self._capabilities.clear()
        self._tools.clear()
        self._permissions.clear()
        self._constraints.clear()
        return self

    def clone(self) -> "CapabilityBuilder":
        builder = CapabilityBuilder()
        builder._capabilities = list(self._capabilities)
        builder._tools = list(self._tools)
        builder._permissions = list(self._permissions)
        builder._constraints = list(self._constraints)
        return builder
