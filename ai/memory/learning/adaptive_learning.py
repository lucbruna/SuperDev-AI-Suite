from __future__ import annotations

from typing import Any


class AdaptiveLearning:
    """Adapts learning behavior based on performance feedback."""

    def __init__(self, initial_rate: float = 0.5):
        self._learning_rate = initial_rate
        self._adaptations: list[dict[str, Any]] = []

    @property
    def learning_rate(self) -> float:
        return self._learning_rate

    @property
    def adaptation_count(self) -> int:
        return len(self._adaptations)

    def adapt(self, performance: float) -> float:
        if performance > 0.8:
            self._learning_rate = min(1.0, self._learning_rate * 1.1)
        elif performance < 0.3:
            self._learning_rate = max(0.01, self._learning_rate * 0.9)
        self._adaptations.append({"performance": performance, "new_rate": self._learning_rate})
        return self._learning_rate

    def reset(self) -> None:
        self._learning_rate = 0.5
        self._adaptations.clear()
