"""Voice Learning — persists preferences and feedback to disk (JSON)."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_LEARNING_FILE = Path(__file__).resolve().parent.parent.parent.parent / "downloads" / "voice" / "learning.json"


class VoiceLearning:
    """Stores user feedback and preferred voices per language."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else _LEARNING_FILE
        self._data: dict[str, Any] = {"preferences": {}, "feedback": []}
        self._load()

    def _load(self) -> None:
        try:
            if self.path.exists():
                with open(self.path, encoding="utf-8") as f:
                    self._data = json.load(f)
        except Exception as e:  # noqa: BLE001
            logger.warning("voice learning load failed: %s", e)

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception as e:  # noqa: BLE001
            logger.warning("voice learning save failed: %s", e)

    def prefer_voice(self, language: str, voice_id: str) -> None:
        lang = language.lower().split("-")[0]
        self._data["preferences"][lang] = voice_id
        self._save()

    def preferred_voice(self, language: str) -> str | None:
        return self._data["preferences"].get(language.lower().split("-")[0])

    def add_feedback(self, voice_id: str, rating: int, text: str = "") -> None:
        self._data["feedback"].append(
            {"voice_id": voice_id, "rating": int(rating), "text": text[:200]}
        )
        self._save()

    def best_voice(self, language: str) -> str | None:
        lang = language.lower().split("-")[0]
        votes: dict[str, list[int]] = {}
        for fb in self._data["feedback"]:
            if fb["voice_id"].startswith(lang) or lang in fb.get("voice_id", ""):
                votes.setdefault(fb["voice_id"], []).append(fb["rating"])
        if not votes:
            return self.preferred_voice(language)
        return max(votes, key=lambda k: sum(votes[k]) / len(votes[k]))
