from __future__ import annotations

from typing import Any


class Summarizer:
    """Creates summaries from memory entries."""

    def __init__(self):
        self._summary_count: int = 0

    @property
    def summary_count(self) -> int:
        return self._summary_count

    def summarize(self, entries: list[dict[str, Any]], max_length: int = 200) -> str:
        if not entries:
            return ""
        parts: list[str] = []
        for entry in entries:
            content = entry.get("content", "")
            if isinstance(content, str):
                parts.append(content[:100])
            elif isinstance(content, dict):
                parts.append(str(list(content.keys())))
        combined = "; ".join(parts)
        self._summary_count += 1
        if len(combined) <= max_length:
            return combined
        return combined[:max_length] + "..."

    def summarize_by_type(self, entries: list[dict[str, Any]]) -> dict[str, str]:
        groups: dict[str, list[str]] = {}
        for entry in entries:
            t = entry.get("type", "unknown")
            content = entry.get("content", "")
            groups.setdefault(t, []).append(str(content)[:80])
        result: dict[str, str] = {}
        for t, items in groups.items():
            result[t] = f"{len(items)} entries: {'; '.join(items[:3])}"
            if len(items) > 3:
                result[t] += f" (+{len(items) - 3} more)"
        self._summary_count += 1
        return result

    def brief(self, entry: dict[str, Any]) -> str:
        content = entry.get("content", "")
        s = str(content)[:120]
        return s + "..." if len(str(content)) > 120 else s

    def reset(self) -> None:
        self._summary_count = 0
