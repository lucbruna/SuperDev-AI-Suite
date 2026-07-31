from __future__ import annotations


class DecisionOptimizer:
    """Optimizes decision selection based on historical outcomes."""

    def __init__(self):
        self._weights: dict[str, float] = {}

    def update_weights(self, option: str, success: bool, delta: float = 0.1) -> None:
        current = self._weights.get(option, 1.0)
        if success:
            self._weights[option] = current + delta
        else:
            self._weights[option] = max(0.1, current - delta)

    def get_weight(self, option: str) -> float:
        return self._weights.get(option, 1.0)

    def rank(self, options: list[str]) -> list[tuple[str, float]]:
        scored = [(opt, self._weights.get(opt, 1.0)) for opt in options]
        return sorted(scored, key=lambda x: x[1], reverse=True)

    def reset(self) -> None:
        self._weights.clear()
