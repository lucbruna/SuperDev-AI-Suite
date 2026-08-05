"""Prompt history — append-only log of processed prompts."""
from __future__ import annotations

import time
import uuid
from typing import Any


class PromptHistory:
    """Records every processed prompt with result and latency."""

    def __init__(self, max_entries: int = 500) -> None:
        self._entries: list[dict[str, Any]] = []
        self.max_entries = max_entries

    def record(self, prompt: str, result: Any = None, *, provider: str | None = None, latency_ms: float = 0.0, ok: bool = True) -> dict[str, Any]:
        entry = {
            "id": str(uuid.uuid4()),
            "prompt": prompt,
            "result": result,
            "provider": provider,
            "latency_ms": round(latency_ms, 2),
            "ok": ok,
            "created_at": time.time(),
        }
        self._entries.append(entry)
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries :]
        return entry

    def list(self, limit: int = 50, provider: str | None = None) -> list[dict[str, Any]]:
        entries = self._entries
        if provider:
            entries = [e for e in entries if e["provider"] == provider]
        return list(reversed(entries[-limit:]))

    def stats(self) -> dict[str, Any]:
        if not self._entries:
            return {"count": 0, "success_rate": 0.0, "avg_latency_ms": 0.0}
        ok_count = sum(1 for e in self._entries if e["ok"])
        avg_latency = sum(e["latency_ms"] for e in self._entries) / len(self._entries)
        return {
            "count": len(self._entries),
            "success_rate": round(ok_count / len(self._entries), 4),
            "avg_latency_ms": round(avg_latency, 2),
        }

    def clear(self) -> int:
        count = len(self._entries)
        self._entries.clear()
        return count


_prompt_history: PromptHistory | None = None


def get_prompt_history() -> PromptHistory:
    global _prompt_history
    if _prompt_history is None:
        _prompt_history = PromptHistory()
    return _prompt_history
