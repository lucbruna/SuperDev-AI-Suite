"""Learning subsystem configuration."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class LearningConfig:
    """Deterministic learning behaviour."""

    pattern_enabled: bool = True
    incident_enabled: bool = True
    feedback_enabled: bool = True
    max_patterns: int = 500
    max_incidents: int = 200
    max_feedback: int = 200
