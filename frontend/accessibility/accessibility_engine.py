from __future__ import annotations

import logging
from typing import Any

from .contrast import ContrastEngine
from .keyboard_navigation import KeyboardNavigation
from .screen_reader import ScreenReader
from .voice_control import VoiceControl


class AccessibilityEngine:
    """Coordinates accessibility features across the frontend."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.accessibility")
        self.keyboard = KeyboardNavigation()
        self.screen_reader = ScreenReader()
        self.contrast = ContrastEngine()
        self.voice = VoiceControl()
        self._enabled = True

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def is_enabled(self) -> bool:
        return self._enabled

    def audit(self, text: str = "", bg: str = "#ffffff", fg: str = "#000000") -> dict[str, Any]:
        return {
            "keyboard_shortcuts": self.keyboard.registered(),
            "contrast_ratio": self.contrast.ratio(bg, fg),
            "text_length": len(text),
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "enabled": self._enabled,
            "shortcuts": self.keyboard.registered(),
            "screen_reader": self.screen_reader.status(),
            "voice": self.voice.status(),
        }
