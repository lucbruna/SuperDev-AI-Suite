"""Personality subsystem for agent behavior customization."""
from __future__ import annotations

from .personality_engine import PersonalityEngine
from .communication_style import CommunicationStyle
from .decision_style import DecisionStyle
from .collaboration_style import CollaborationStyle

__all__ = [
    "PersonalityEngine",
    "CommunicationStyle",
    "DecisionStyle",
    "CollaborationStyle",
]
