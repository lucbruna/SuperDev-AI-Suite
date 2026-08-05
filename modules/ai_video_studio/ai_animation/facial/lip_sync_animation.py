"""Lip sync animation — map speech audio to mouth shapes."""
from __future__ import annotations

import re
from typing import Any


class LipSyncAnimation:
    """Converts text/visemes into timed mouth-shape events."""

    _VISEMES = {
        "a": "open", "e": "grin", "i": "grin", "o": "round",
        "u": "round", "m": "closed", "b": "closed", "p": "closed",
    }

    def visemes_for(self, text: str) -> list[dict[str, Any]]:
        words = re.findall(r"[a-z']+", text.lower())
        events: list[dict[str, Any]] = []
        for i, word in enumerate(words):
            if not word:
                continue
            first = word[0]
            events.append(
                {
                    "word_index": i,
                    "word": word,
                    "viseme": self._VISEMES.get(first, "closed"),
                    "start_word": i,
                }
            )
        return events

    def timeline(self, text: str, *, fps: int = 24, words_per_second: float = 2.5) -> list[dict[str, Any]]:
        events = self.visemes_for(text)
        per_word_frames = max(1, int(fps / words_per_second))
        timeline = []
        for event in events:
            timeline.append(
                {
                    "frame": event["word_index"] * per_word_frames,
                    "shape": event["viseme"],
                    "word": event["word"],
                }
            )
        return timeline
