from __future__ import annotations

from typing import Any, Dict, List, Optional


class AgentMemory:
    """Memory storage for agents."""

    def __init__(self, max_size: int = 100) -> None:
        self._max_size = max_size
        self._short_term: List[Dict[str, Any]] = []
        self._long_term: Dict[str, Any] = {}

    def remember(self, key: str, value: Any) -> None:
        self._short_term.append({"key": key, "value": value})
        if len(self._short_term) > self._max_size:
            self._short_term.pop(0)
        self._long_term[key] = value

    def recall(self, key: str) -> Optional[Any]:
        return self._long_term.get(key)

    def forget(self, key: str) -> bool:
        self._short_term = [s for s in self._short_term if s["key"] != key]
        return self._long_term.pop(key, None) is not None

    def clear(self) -> None:
        self._short_term.clear()
        self._long_term.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "short_term_count": len(self._short_term),
            "long_term_count": len(self._long_term),
        }
