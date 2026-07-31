"""Token optimization."""
from __future__ import annotations
from typing import Any, Dict, List

class TokenOptimizer:
    def __init__(self, max_tokens: int = 4096) -> None:
        self._max_tokens = max_tokens
        self._history: List[Dict[str, Any]] = []
    def count_tokens(self, text: str) -> int:
        return len(text) // 4
    def optimize(self, text: str, target_tokens: int = None) -> Dict[str, Any]:
        target = target_tokens or self._max_tokens
        current = self.count_tokens(text)
        if current <= target:
            return {"text": text, "tokens": current, "optimized": False, "savings": 0}
        ratio = target / current
        optimized = text[:int(len(text) * ratio * 0.9)]
        savings = (current - self.count_tokens(optimized)) / current
        result = {"text": optimized, "tokens": self.count_tokens(optimized), "original_tokens": current, "optimized": True, "savings": savings}
        self._history.append(result)
        return result
    def truncate(self, text: str, max_tokens: int) -> str:
        max_chars = max_tokens * 4
        return text[:max_chars] if len(text) > max_chars else text
    def summarize_tokens(self, texts: List[str]) -> Dict[str, Any]:
        tokens = [self.count_tokens(t) for t in texts]
        return {"total": sum(tokens), "avg": sum(tokens) / len(tokens) if tokens else 0, "min": min(tokens) if tokens else 0, "max": max(tokens) if tokens else 0}
    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._history[-limit:]
    def count(self) -> int:
        return len(self._history)
