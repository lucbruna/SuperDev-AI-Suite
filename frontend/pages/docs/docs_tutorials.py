from __future__ import annotations

import logging
from typing import Any


class DocsTutorials:
    """Guided tutorials with progress tracking."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.docs.tutorials")
        self._tutorials: dict[str, dict[str, Any]] = {}
        self._progress: dict[str, int] = {}

    def render(self) -> dict[str, Any]:
        return {"tutorials": self.list(), "count": len(self._tutorials)}

    def list(self) -> list[dict[str, Any]]:
        return [
            {"tutorial_id": tutorial_id, **tutorial}
            for tutorial_id, tutorial in self._tutorials.items()
        ]

    def start(self, tutorial_id: str) -> dict[str, Any]:
        tutorial = self._tutorials.get(tutorial_id)
        if tutorial is None:
            raise KeyError(f"unknown tutorial: {tutorial_id}")
        self._progress[tutorial_id] = 1
        return {"tutorial_id": tutorial_id, "step": 1, **tutorial}

    def progress(self, tutorial_id: str) -> dict[str, Any]:
        steps = self._tutorials.get(tutorial_id, {}).get("steps", 1)
        current = self._progress.get(tutorial_id, 0)
        return {
            "tutorial_id": tutorial_id,
            "step": current,
            "total": steps,
            "percent": round(current / steps * 100, 1),
        }
