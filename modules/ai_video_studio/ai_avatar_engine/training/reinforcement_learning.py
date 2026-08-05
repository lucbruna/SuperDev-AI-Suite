"""Reinforcement learning — reward-driven action selection (multi-armed bandit)."""
from __future__ import annotations

from typing import Any


class ReinforcementLearning:
    """Simple epsilon-greedy bandit over named actions."""

    def __init__(self, epsilon: float = 0.1) -> None:
        self.epsilon = max(0.0, min(1.0, epsilon))
        self._rewards: dict[str, list[float]] = {}

    def choose(self, actions: list[str]) -> str:
        if not actions:
            raise ValueError("no actions available")
        if len(actions) == 1:
            return actions[0]
        if all(a not in self._rewards for a in actions) or self._explore():
            import random

            return random.choice(actions)
        best = max(actions, key=lambda a: sum(self._rewards.get(a, [0.0])) / max(len(self._rewards.get(a, [])), 1))
        return best

    def reward(self, action: str, reward: float) -> None:
        self._rewards.setdefault(action, []).append(float(reward))

    def _explore(self) -> bool:
        import random

        return random.random() < self.epsilon

    def stats(self) -> dict[str, Any]:
        return {
            action: {"count": len(r), "avg": round(sum(r) / len(r), 3) if r else 0.0}
            for action, r in self._rewards.items()
        }


_reinforcement_learning: ReinforcementLearning | None = None


def get_reinforcement_learning() -> ReinforcementLearning:
    global _reinforcement_learning
    if _reinforcement_learning is None:
        _reinforcement_learning = ReinforcementLearning()
    return _reinforcement_learning
