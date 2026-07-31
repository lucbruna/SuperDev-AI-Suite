from __future__ import annotations

from typing import Any


class SupervisedLearning:
    """Supervised learning using labeled training data."""

    def __init__(self):
        self._training_data: list[tuple[Any, Any]] = []
        self._train_count: int = 0

    @property
    def training_data(self) -> list[tuple[Any, Any]]:
        return list(self._training_data)

    @property
    def train_count(self) -> int:
        return self._train_count

    def add_example(self, features: Any, label: Any) -> None:
        self._training_data.append((features, label))

    def add_batch(self, examples: list[tuple[Any, Any]]) -> None:
        self._training_data.extend(examples)

    def predict(self, features: Any) -> Any:
        if not self._training_data:
            return None
        best_example = self._training_data[0]
        best_score = -1.0
        for ex_features, ex_label in self._training_data:
            sim = self._similarity(features, ex_features)
            if sim > best_score:
                best_score = sim
                best_example = ex_label
        self._train_count += 1
        return best_example

    def _similarity(self, a: Any, b: Any) -> float:
        if isinstance(a, dict) and isinstance(b, dict):
            keys_a = set(a.keys())
            keys_b = set(b.keys())
            if not keys_a and not keys_b:
                return 1.0
            return len(keys_a & keys_b) / max(len(keys_a | keys_b), 1)
        return 1.0 if str(a) == str(b) else 0.0

    def clear(self) -> None:
        self._training_data.clear()
        self._train_count = 0
