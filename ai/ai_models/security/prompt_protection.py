"""Prompt protection."""
from __future__ import annotations
from typing import Any, Dict, List

class PromptProtector:
    def __init__(self) -> None:
        self._filters: List[Dict[str, Any]] = []
        self._blocked: List[Dict[str, Any]] = []
    def add_filter(self, name: str, pattern: str, action: str = "block") -> Dict[str, Any]:
        f = {"name": name, "pattern": pattern, "action": action}
        self._filters.append(f)
        return f
    def check(self, prompt: str) -> Dict[str, Any]:
        for f in self._filters:
            if f["pattern"].lower() in prompt.lower():
                self._blocked.append({"prompt": prompt[:100], "filter": f["name"], "action": f["action"]})
                return {"safe": False, "filter": f["name"], "action": f["action"]}
        return {"safe": True}
    def sanitize(self, prompt: str) -> str:
        result = prompt
        for f in self._filters:
            if f["action"] == "remove":
                result = result.replace(f["pattern"], "")
        return result
    def list_filters(self) -> List[Dict[str, Any]]:
        return self._filters
    def remove_filter(self, name: str) -> bool:
        original = len(self._filters)
        self._filters = [f for f in self._filters if f["name"] != name]
        return len(self._filters) < original
    def get_blocked(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._blocked[-limit:]
    def count(self) -> int:
        return len(self._filters)
    def clear(self) -> int:
        n = len(self._filters)
        self._filters.clear()
        return n
