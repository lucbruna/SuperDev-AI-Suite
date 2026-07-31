"""Token manager."""
from __future__ import annotations
from typing import Any, Dict

class TokenManager:
    def __init__(self, max_tokens: int = 4096) -> None:
        self._max = max_tokens
        self._usage: Dict[str, int] = {}
    def count_tokens(self, text: str) -> int:
        return len(text.split())
    def truncate(self, text: str, max_tokens: int = 0) -> str:
        limit = max_tokens or self._max
        tokens = text.split()
        if len(tokens) <= limit:
            return text
        return " ".join(tokens[:limit])
    def remaining(self, text: str) -> int:
        used = self.count_tokens(text)
        return max(0, self._max - used)
    def can_fit(self, text: str, additional: int = 0) -> bool:
        return self.count_tokens(text) + additional <= self._max
    def record_usage(self, model_id: str, tokens: int) -> None:
        self._usage[model_id] = self._usage.get(model_id, 0) + tokens
    def get_usage(self, model_id: str = "") -> int:
        if model_id:
            return self._usage.get(model_id, 0)
        return sum(self._usage.values())
    def set_max(self, max_tokens: int) -> None:
        self._max = max_tokens
    def get_max(self) -> int:
        return self._max
    def get_usage_by_model(self) -> Dict[str, int]:
        return dict(self._usage)
