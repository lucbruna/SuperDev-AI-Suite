"""Translation Learning — records corrections and preferred style."""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_LEARNING_FILE = Path(__file__).resolve().parent.parent.parent.parent / "downloads" / "translation_learning.json"


class TranslationLearning:
    """Stores corrections so future translations can prefer them."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else _LEARNING_FILE
        self._data: dict[str, Any] = {"corrections": [], "style": {}}
        self._load()

    def _load(self) -> None:
        try:
            if self.path.exists():
                with open(self.path, encoding="utf-8") as f:
                    self._data = json.load(f)
        except Exception as e:  # noqa: BLE001
            logger.warning("translation learning load failed: %s", e)

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception as e:  # noqa: BLE001
            logger.warning("translation learning save failed: %s", e)

    def add_correction(self, source: str, target: str, original: str, corrected: str) -> None:
        self._data["corrections"].append({
            "source": source, "target": target, "original": original,
            "corrected": corrected, "ts": time.time(),
        })
        self._save()

    def corrections(self) -> list[dict[str, Any]]:
        return list(self._data["corrections"])

    def set_style(self, target: str, style: str) -> None:
        self._data["style"][target.lower()] = style
        self._save()

    def style(self, target: str) -> str | None:
        return self._data["style"].get(target.lower())
