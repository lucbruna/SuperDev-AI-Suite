"""Voice Statistics — aggregates synthesis metrics in-memory."""
from __future__ import annotations

import time
from collections import Counter
from typing import Any

_STATS = None


def get_voice_statistics() -> VoiceStatistics:
    global _STATS
    if _STATS is None:
        _STATS = VoiceStatistics()
    return _STATS


class VoiceStatistics:
    """Tracks synthesis events, engines used, durations and languages."""

    def __init__(self) -> None:
        self._total = 0
        self._total_seconds = 0.0
        self._engines: Counter[str] = Counter()
        self._languages: Counter[str] = Counter()
        self._history: list[dict[str, Any]] = []
        self._started = time.time()

    def record(self, *, engine: str, language: str, duration: float) -> None:
        self._total += 1
        self._total_seconds += duration
        self._engines[engine] += 1
        self._languages[language.lower().split("-")[0]] += 1
        self._history.append(
            {"engine": engine, "language": language, "duration": duration, "ts": time.time()}
        )
        if len(self._history) > 500:
            self._history = self._history[-500:]

    def snapshot(self) -> dict[str, Any]:
        return {
            "total_synthesized": self._total,
            "total_audio_seconds": round(self._total_seconds, 2),
            "uptime_seconds": round(time.time() - self._started, 1),
            "engines": dict(self._engines),
            "languages": dict(self._languages),
            "recent": self._history[-10:],
        }
