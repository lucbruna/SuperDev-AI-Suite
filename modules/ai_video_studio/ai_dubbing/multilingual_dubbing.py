"""Multilingual Dubbing — dub one video into several languages."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_dubbing.dubbing_engine import get_dubbing_engine


class MultilingualDubbing:
    """Runs the dubbing pipeline for each requested language."""

    def __init__(self) -> None:
        self.engine = get_dubbing_engine()

    def dub_many(self, video_path: str, languages: list[str], *,
                 source_transcript: str | None = None,
                 source_language: str | None = None) -> dict[str, Any]:
        results: dict[str, Any] = {}
        for language in languages:
            results[language] = self.engine.dub(
                video_path, language,
                source_transcript=source_transcript, source_language=source_language,
            )
        return {"languages": results, "count": len(results)}
