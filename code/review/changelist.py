from __future__ import annotations

import logging
from typing import Any


class ChangeList:
    """Tracks changes made during review."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.review.changelist")
        self._changes: list[dict[str, Any]] = []

    def add_change(self, file: str, change_type: str, description: str) -> None:
        self._changes.append({"file": file, "type": change_type, "description": description})

    def get_changes(self) -> list[dict[str, Any]]:
        return list(self._changes)

    def clear(self) -> None:
        self._changes.clear()
