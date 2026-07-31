"""Personality engine for agent behavior customization."""

from __future__ import annotations

from typing import Any

from .collaboration_style import CollaborationStyle
from .communication_style import CommunicationStyle
from .decision_style import DecisionStyle


class PersonalityEngine:
    """Manages agent personality traits and behavioral patterns."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {}
        self._communication = CommunicationStyle(
            tone=self._config.get("tone", "professional"),
            verbosity=self._config.get("verbosity", "moderate"),
        )
        self._decision = DecisionStyle(
            risk_tolerance=self._config.get("risk_tolerance", 0.5),
            analysis_depth=self._config.get("analysis_depth", "balanced"),
        )
        self._collaboration = CollaborationStyle(
            style=self._config.get("collaboration_style", "cooperative"),
            leadership=self._config.get("leadership", False),
        )

    def get_personality(self) -> dict[str, Any]:
        return {
            "communication": self._communication.get_profile(),
            "decision": self._decision.get_profile(),
            "collaboration": self._collaboration.get_profile(),
        }

    def adjust_trait(self, trait: str, value: Any) -> None:
        if trait == "tone":
            self._communication.set_tone(value)
        elif trait == "verbosity":
            self._communication.set_verbosity(value)
        elif trait == "risk_tolerance":
            self._decision.set_risk_tolerance(value)
        elif trait == "analysis_depth":
            self._decision.set_analysis_depth(value)
        elif trait == "collaboration_style":
            self._collaboration.set_style(value)
        elif trait == "leadership":
            self._collaboration.set_leadership(value)

    def get_snapshot(self) -> dict[str, Any]:
        return self.get_personality()
