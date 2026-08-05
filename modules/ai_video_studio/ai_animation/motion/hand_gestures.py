"""Hand gestures — library of communicative hand gestures."""
from __future__ import annotations

from typing import Any

_GESTURES = ("point", "wave", "thumbs_up", "ok", "clap", "grab")


class HandGestures:
    """Provides gesture definitions for hand animation."""

    def gesture(self, name: str) -> dict[str, Any]:
        if name not in _GESTURES:
            raise ValueError(f"Unknown gesture '{name}'")
        return {"gesture": name, "finger_curls": 0.5, "wrist_rotation": 0.0}

    def available(self) -> list[str]:
        return list(_GESTURES)
