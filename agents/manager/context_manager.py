from __future__ import annotations

import json
from typing import Any, Optional


class ContextManager:
    def __init__(self, max_tokens: int = 8192) -> None:
        self._max_tokens = max_tokens

    def build_context(
        self,
        agent_id: str,
        task: str,
        project_context: Optional[dict[str, Any]] = None,
        user_context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        merged: dict[str, Any] = {
            "agent_id": agent_id,
            "task": task,
        }

        if project_context:
            merged["project"] = project_context
        if user_context:
            merged["user"] = user_context

        merged["metadata"] = {
            "timestamp": __import__("time").time(),
            "token_limit": self._max_tokens,
        }

        context_size = self._estimate_tokens(str(merged))
        if context_size > self._max_tokens:
            merged = self._truncate_context(merged, context_size)

        return merged

    def _estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def _truncate_context(self, context: dict[str, Any], current_size: int) -> dict[str, Any]:
        ratio = self._max_tokens / current_size
        serialized = json.dumps(context)
        target_len = int(len(serialized) * ratio)
        truncated = serialized[:target_len]
        return json.loads(truncated) if truncated else context

    def merge_contexts(self, *contexts: dict[str, Any]) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        for ctx in contexts:
            merged.update(ctx)
        return merged
