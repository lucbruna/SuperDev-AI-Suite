from __future__ import annotations

import time
import uuid
from typing import Any


class ToolLogger:
    """Logs tool operations for audit and debugging."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def log(self, level: str, tool_name: str, message: str, **kwargs: Any) -> str:
        entry_id = str(uuid.uuid4())
        entry: dict[str, Any] = {
            "id": entry_id,
            "timestamp": time.time(),
            "level": level,
            "tool": tool_name,
            "message": message,
        }
        entry.update(kwargs)
        self._entries.append(entry)
        return entry_id

    def info(self, tool_name: str, message: str, **kwargs: Any) -> str:
        return self.log("info", tool_name, message, **kwargs)

    def warn(self, tool_name: str, message: str, **kwargs: Any) -> str:
        return self.log("warn", tool_name, message, **kwargs)

    def error(self, tool_name: str, message: str, **kwargs: Any) -> str:
        return self.log("error", tool_name, message, **kwargs)

    def debug(self, tool_name: str, message: str, **kwargs: Any) -> str:
        return self.log("debug", tool_name, message, **kwargs)

    def get_entries(self, tool_name: str | None = None, level: str | None = None) -> list[dict[str, Any]]:
        results = self._entries
        if tool_name:
            results = [e for e in results if e["tool"] == tool_name]
        if level:
            results = [e for e in results if e["level"] == level]
        return results

    def get_recent(self, count: int = 10) -> list[dict[str, Any]]:
        return self._entries[-count:]

    def clear(self) -> None:
        self._entries.clear()

    @property
    def entry_count(self) -> int:
        return len(self._entries)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_entries": self.entry_count,
            "recent": self.get_recent(10),
        }
