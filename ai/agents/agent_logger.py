from __future__ import annotations

import time
from typing import Any, Dict, List


class AgentLogger:
    """Logging for agent operations."""

    def __init__(self, max_entries: int = 1000) -> None:
        self._entries: List[Dict[str, Any]] = []
        self._max_entries = max_entries

    def log(self, level: str, agent_id: str, message: str) -> None:
        entry = {
            "level": level,
            "agent_id": agent_id,
            "message": message,
            "timestamp": time.time(),
        }
        self._entries.append(entry)
        if len(self._entries) > self._max_entries:
            self._entries.pop(0)

    def info(self, agent_id: str, message: str) -> None:
        self.log("INFO", agent_id, message)

    def warn(self, agent_id: str, message: str) -> None:
        self.log("WARN", agent_id, message)

    def error(self, agent_id: str, message: str) -> None:
        self.log("ERROR", agent_id, message)

    def get_entries(self, level: str = "") -> List[Dict[str, Any]]:
        if not level:
            return list(self._entries)
        return [e for e in self._entries if e["level"] == level]

    def clear(self) -> None:
        self._entries.clear()
