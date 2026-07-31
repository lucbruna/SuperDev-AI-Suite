"""Collaboration style management."""
from __future__ import annotations

from typing import Any, Dict, List


class CollaborationStyle:
    """Defines how an agent collaborates within teams."""

    def __init__(self, style: str = "cooperative", leadership: bool = False) -> None:
        self._style = style
        self._leadership = leadership
        self._valid_styles = ["cooperative", "competitive", "autonomous", "supportive"]

    def set_style(self, style: str) -> None:
        if style in self._valid_styles:
            self._style = style

    def set_leadership(self, leadership: bool) -> None:
        self._leadership = bool(leadership)

    def get_profile(self) -> Dict[str, Any]:
        return {
            "style": self._style,
            "leadership": self._leadership,
            "proactive": self._leadership or self._style == "cooperative",
            "delegates": self._leadership and self._style in ("cooperative", "supportive"),
        }

    def assign_role(self, team_tasks: List[Dict[str, Any]]) -> str:
        if self._leadership:
            return "lead"
        if self._style == "supportive":
            return "support"
        if self._style == "autonomous":
            return "independent"
        return "collaborator"
