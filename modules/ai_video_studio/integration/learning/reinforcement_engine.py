"""Reinforcement Engine — epsilon-greedy contextual bandit."""
from __future__ import annotations

import random
from typing import Any


class ReinforcementEngine:
    """Learns which option performs best from reward feedback."""

    def __init__(self, epsilon: float = 0.1, seed: int = 42) -> None:
        self.epsilon = epsilon
        self._rng = random.Random(seed)
        self._rewards: dict[str, dict[str, float]] = {}

    def choose(self, options: list[str]) -> dict[str, Any]:
        """Pick an option (explore vs exploit)."""
        if not options:
            return {"ok": False, "error": "no options"}
        if self._rng.random() < self.epsilon:
            choice = self._rng.choice(options)
            mode = "explore"
        else:
            choice = max(options, key=lambda o: self._estimate(o))
            mode = "exploit"
        return {"choice": choice, "mode": mode, "estimates": {
            o: round(self._estimate(o), 3) for o in options}}

    def reward(self, option: str, value: float) -> dict[str, Any]:
        stats = self._rewards.setdefault(option, {"n": 0.0, "sum": 0.0})
        stats["n"] += 1
        stats["sum"] += value
        return {"option": option, "estimate": round(self._estimate(option), 3)}

    def _estimate(self, option: str) -> float:
        stats = self._rewards.get(option)
        return stats["sum"] / stats["n"] if stats and stats["n"] else 0.5


_reinforcement_engine: ReinforcementEngine | None = None


def get_reinforcement_engine() -> ReinforcementEngine:
    global _reinforcement_engine
    if _reinforcement_engine is None:
        _reinforcement_engine = ReinforcementEngine()
    return _reinforcement_engine
