"""Preference learning — models director and audience preferences."""
from __future__ import annotations



class PreferenceLearning:
    """Stores preference weights for decision factors."""

    def __init__(self) -> None:
        self._preferences: dict[str, float] = {}

    def set(self, key: str, value: float) -> None:
        self._preferences[key] = max(0.0, min(1.0, value))

    def get(self, key: str, default: float = 0.5) -> float:
        return self._preferences.get(key, default)


_preference_learning: PreferenceLearning | None = None


def get_preference_learning() -> PreferenceLearning:
    global _preference_learning
    if _preference_learning is None:
        _preference_learning = PreferenceLearning()
    return _preference_learning
