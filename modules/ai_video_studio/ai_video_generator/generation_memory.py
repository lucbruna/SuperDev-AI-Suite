"""Generation memory — remember past prompts, params and outcomes."""
from __future__ import annotations

import time
from typing import Any


class GenerationMemory:
    """Bounded memory of prior generation requests for reuse and learning."""

    def __init__(self, max_entries: int = 1000) -> None:
        self.max_entries = max_entries
        self._entries: list[dict[str, Any]] = []

    def remember(
        self,
        *,
        mode: str,
        prompt: str,
        params: dict[str, Any],
        output_ref: str,
        quality: float | None = None,
    ) -> None:
        entry: dict[str, Any] = {
            "mode": mode,
            "prompt": prompt,
            "params": params,
            "output_ref": output_ref,
            "quality": quality,
            "timestamp": time.time(),
        }
        self._entries.append(entry)
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries :]

    def find_similar(self, prompt: str, *, mode: str | None = None, limit: int = 5) -> list[dict[str, Any]]:
        """Return the most recently remembered entries sharing tokens with prompt."""
        prompt_tokens = {w.lower() for w in prompt.split()}
        scored: list[tuple[int, dict[str, Any]]] = []
        for entry in self._entries:
            if mode is not None and entry["mode"] != mode:
                continue
            entry_tokens = {w.lower() for w in entry["prompt"].split()}
            overlap = len(prompt_tokens & entry_tokens)
            if overlap:
                scored.append((overlap, entry))
        scored.sort(key=lambda item: (item[0], item[1]["timestamp"]), reverse=True)
        return [entry for _, entry in scored[:limit]]

    def count(self) -> int:
        return len(self._entries)

    def clear(self) -> None:
        self._entries.clear()


_generation_memory: GenerationMemory | None = None


def get_generation_memory() -> GenerationMemory:
    global _generation_memory
    if _generation_memory is None:
        _generation_memory = GenerationMemory()
    return _generation_memory
