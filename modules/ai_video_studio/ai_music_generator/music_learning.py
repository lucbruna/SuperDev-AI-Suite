"""Music Learning — records genre usage and preferences."""
from __future__ import annotations

import json
import logging
import time
from collections import Counter
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_LEARNING_FILE = Path(__file__).resolve().parent.parent.parent.parent / "downloads" / "music_learning.json"


class MusicLearning:
    """Tracks which genres users actually generate."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else _LEARNING_FILE
        self._data: dict[str, Any] = {"genre_usage": {}, "history": []}
        self._load()

    def _load(self) -> None:
        try:
            if self.path.exists():
                with open(self.path, encoding="utf-8") as f:
                    self._data = json.load(f)
        except Exception as e:  # noqa: BLE001
            logger.warning("music learning load failed: %s", e)

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception as e:  # noqa: BLE001
            logger.warning("music learning save failed: %s", e)

    def record_generation(self, genre: str, duration: float) -> None:
        usage = Counter(self._data.get("genre_usage", {}))
        usage[genre] += 1
        self._data["genre_usage"] = dict(usage)
        self._data["history"].append({"genre": genre, "duration": duration, "ts": time.time()})
        self._data["history"] = self._data["history"][-200:]
        self._save()

    def favorite_genres(self, top: int = 3) -> list[tuple[str, int]]:
        return Counter(self._data.get("genre_usage", {})).most_common(top)
