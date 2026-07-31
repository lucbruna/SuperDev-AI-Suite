from __future__ import annotations


class ReinforcementLearning:
    """Reinforcement learning from action-reward cycles."""

    def __init__(self, learning_rate: float = 0.1):
        self._q_table: dict[str, float] = {}
        self._learning_rate = learning_rate
        self._cycle_count: int = 0

    @property
    def learning_rate(self) -> float:
        return self._learning_rate

    @property
    def cycle_count(self) -> int:
        return self._cycle_count

    def act(self, state: str, actions: list[str]) -> str:
        best_action = actions[0]
        best_value = float("-inf")
        for action in actions:
            key = f"{state}:{action}"
            value = self._q_table.get(key, 0.0)
            if value > best_value:
                best_value = value
                best_action = action
        self._cycle_count += 1
        return best_action

    def reward(self, state: str, action: str, reward_val: float) -> None:
        key = f"{state}:{action}"
        current = self._q_table.get(key, 0.0)
        self._q_table[key] = current + self._learning_rate * (reward_val - current)

    def get_q_value(self, state: str, action: str) -> float:
        return self._q_table.get(f"{state}:{action}", 0.0)

    def clear(self) -> None:
        self._q_table.clear()
        self._cycle_count = 0
