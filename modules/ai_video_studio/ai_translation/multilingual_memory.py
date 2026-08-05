"""Multilingual Memory — translation memory (TM) with exact-match lookup."""
from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_TM_FILE = Path(__file__).resolve().parent.parent.parent.parent / "downloads" / "translation_memory.json"


class MultilingualMemory:
    """Caches ``(source_lang, target_lang, source_text) → translation``."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else _TM_FILE
        self._memory: dict[str, dict[str, str]] = {}
        self._load()

    def _load(self) -> None:
        try:
            if self.path.exists():
                with open(self.path, encoding="utf-8") as f:
                    self._memory = json.load(f)
        except Exception as e:  # noqa: BLE001
            logger.warning("TM load failed: %s", e)

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._memory, f, ensure_ascii=False, indent=2)
        except Exception as e:  # noqa: BLE001
            logger.warning("TM save failed: %s", e)

    @staticmethod
    def _key(source: str, target: str, text: str) -> str:
        digest = hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()[:16]
        return f"{source.lower()}:{target.lower()}:{digest}"

    def get(self, source: str, target: str, text: str) -> str | None:
        return self._memory.get(self._key(source, target, text))

    def store(self, source: str, target: str, text: str, translation: str) -> None:
        self._memory[self._key(source, target, text)] = translation
        if len(self._memory) > 10_000:
            keys = list(self._memory)[:2000]
            for k in keys:
                del self._memory[k]
        self._save()

    def stats(self) -> dict[str, Any]:
        return {"entries": len(self._memory), "path": str(self.path)}
