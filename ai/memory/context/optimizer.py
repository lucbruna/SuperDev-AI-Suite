from __future__ import annotations

from typing import Any


class ContextOptimizer:
    """Optimizes context data for size, relevance, and structure."""

    def __init__(self):
        self._optimization_count: int = 0

    @property
    def optimization_count(self) -> int:
        return self._optimization_count

    def trim_duplicates(self, context: dict[str, Any]) -> dict[str, Any]:
        content = context.get("content", {})
        seen: set = set()
        deduped: dict[str, Any] = {}
        for key, value in content.items():
            h = str(value)
            if h not in seen:
                seen.add(h)
                deduped[key] = value
        result = dict(context)
        result["content"] = deduped
        result["metadata"] = dict(result.get("metadata", {}))
        result["metadata"]["deduped"] = True
        self._optimization_count += 1
        return result

    def truncate_content(self, context: dict[str, Any], max_chars: int = 10000) -> dict[str, Any]:
        content = context.get("content", {})
        truncated: dict[str, Any] = {}
        total = 0
        for key, value in content.items():
            s = str(value)
            if total + len(s) > max_chars:
                remaining = max_chars - total
                truncated[key] = s[:remaining] if remaining > 0 else ""
                break
            truncated[key] = s
            total += len(s)
        result = dict(context)
        result["content"] = truncated
        result["metadata"] = dict(result.get("metadata", {}))
        result["metadata"]["truncated"] = True
        self._optimization_count += 1
        return result

    def optimize(self, context: dict[str, Any]) -> dict[str, Any]:
        result = self.trim_duplicates(context)
        result = self.truncate_content(result)
        result["metadata"]["optimized"] = True
        return result

    def reset(self) -> None:
        self._optimization_count = 0
