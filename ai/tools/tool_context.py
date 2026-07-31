from __future__ import annotations

import uuid
from typing import Any

from .tool_models import ToolContext as ToolContextModel


class ToolContext:
    """Manages execution context for tool operations."""

    def __init__(self) -> None:
        self._contexts: dict[str, ToolContextModel] = {}

    def create_context(self, user_id: str = "", session_id: str = "") -> ToolContextModel:
        ctx = ToolContextModel(
            execution_id=str(uuid.uuid4()),
            user_id=user_id,
            session_id=session_id,
        )
        self._contexts[ctx.execution_id] = ctx
        return ctx

    def get_context(self, execution_id: str) -> ToolContextModel | None:
        return self._contexts.get(execution_id)

    def update_context(self, execution_id: str, **kwargs: Any) -> bool:
        ctx = self._contexts.get(execution_id)
        if ctx is None:
            return False
        for key, value in kwargs.items():
            if hasattr(ctx, key):
                setattr(ctx, key, value)
        return True

    def set_environment(self, execution_id: str, env: dict[str, Any]) -> bool:
        ctx = self._contexts.get(execution_id)
        if ctx is None:
            return False
        ctx.environment = env
        return True

    def add_metadata(self, execution_id: str, key: str, value: Any) -> bool:
        ctx = self._contexts.get(execution_id)
        if ctx is None:
            return False
        ctx.metadata[key] = value
        return True

    def remove_context(self, execution_id: str) -> bool:
        if execution_id in self._contexts:
            del self._contexts[execution_id]
            return True
        return False

    @property
    def active_count(self) -> int:
        return len(self._contexts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "active_count": self.active_count,
            "execution_ids": list(self._contexts.keys()),
        }
