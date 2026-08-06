"""Persistent memory for the AI Evolution Engine (atomic JSON)."""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class EvolutionMemory:
    """Key-value memory persisted atomically to a JSON file."""

    memory_file: str = ""
    max_entries: int = 1000
    _entries: dict[str, object] = field(default_factory=dict)

    def remember(self, key: str, value: object) -> None:
        self._entries[key] = value
        self._prune()

    def recall(self, key: str, default: object = None) -> object:
        return self._entries.get(key, default)

    def forget(self, key: str) -> None:
        self._entries.pop(key, None)

    def keys(self) -> list[str]:
        return list(self._entries)

    def entries(self) -> dict[str, object]:
        return dict(self._entries)

    def save(self, path: str | Path | None = None) -> None:
        target = Path(path or self.memory_file)
        if not target:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(target.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(self._entries, handle, ensure_ascii=False, indent=2)
            os.replace(tmp, target)
        except OSError as exc:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise OSError(f"failed to save evolution memory: {exc}") from exc

    def load(self, path: str | Path | None = None) -> None:
        target = Path(path or self.memory_file)
        if not target or not target.exists():
            return
        try:
            with target.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise OSError(f"failed to load evolution memory: {exc}") from exc
        if isinstance(payload, dict):
            self._entries = payload

    def _prune(self) -> None:
        if len(self._entries) > self.max_entries:
            for key in list(self._entries)[: len(self._entries) - self.max_entries]:
                self._entries.pop(key, None)
