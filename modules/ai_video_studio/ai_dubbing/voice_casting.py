"""Voice Casting — assigns voices to characters for multi-actor dubbing."""
from __future__ import annotations

from modules.ai_video_studio.ai_dubbing.actor_selector import select_voice


class VoiceCasting:
    """Keeps a character → voice map, auto-selecting when needed."""

    def __init__(self, language: str = "en") -> None:
        self.language = language
        self._cast: dict[str, str] = {}

    def cast(self, character: str, *, voice_id: str | None = None,
             role: str | None = None, gender: str | None = None) -> str:
        """Assign (or resolve) a voice for a character."""
        if voice_id:
            self._cast[character] = voice_id
        else:
            self._cast[character] = select_voice(role, gender, self.language)
        return self._cast[character]

    def voice_for(self, character: str) -> str:
        return self._cast.get(character, select_voice(language=self.language))

    def mapping(self) -> dict[str, str]:
        return dict(self._cast)
