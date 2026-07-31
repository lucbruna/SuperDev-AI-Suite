"""Communication style management."""
from __future__ import annotations

from typing import Any


class CommunicationStyle:
    """Defines how an agent communicates with users and other agents."""

    def __init__(self, tone: str = "professional", verbosity: str = "moderate") -> None:
        self._tone = tone
        self._verbosity = verbosity
        self._valid_tones = ["professional", "casual", "friendly", "formal", "technical"]
        self._valid_verbs = ["minimal", "moderate", "detailed"]

    def set_tone(self, tone: str) -> None:
        if tone in self._valid_tones:
            self._tone = tone

    def set_verbosity(self, verbosity: str) -> None:
        if verbosity in self._valid_verbs:
            self._verbosity = verbosity

    def get_profile(self) -> dict[str, Any]:
        return {
            "tone": self._tone,
            "verbosity": self._verbosity,
            "explanations": self._verbosity in ("moderate", "detailed"),
            "code_comments": self._verbosity == "detailed",
        }

    def format_response(self, message: str) -> str:
        if self._tone == "formal":
            return message
        if self._tone == "casual":
            return message.lower()
        return message
