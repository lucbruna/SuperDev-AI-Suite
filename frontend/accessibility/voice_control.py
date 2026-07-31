from __future__ import annotations

import logging
from typing import Any, Callable


class VoiceControl:
    """Maps voice commands to frontend actions."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.accessibility.voice")
        self._commands: dict[str, Callable[..., None]] = {}
        self._listening = False

    def add_command(self, phrase: str, handler: Callable[..., None]) -> None:
        self._commands[phrase.lower()] = handler

    def remove_command(self, phrase: str) -> bool:
        return self._commands.pop(phrase.lower(), None) is not None

    def listen(self) -> bool:
        self._listening = True
        return True

    def stop(self) -> bool:
        self._listening = False
        return True

    def is_listening(self) -> bool:
        return self._listening

    def process(self, transcript: str) -> str | None:
        phrase = transcript.strip().lower()
        for command, handler in self._commands.items():
            if command in phrase:
                handler()
                return command
        return None

    def commands(self) -> list[str]:
        return list(self._commands)

    def status(self) -> dict[str, Any]:
        return {"listening": self._listening, "commands": self.commands()}
