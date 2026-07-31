"""k-Nearest Neighbors classification."""

from __future__ import annotations

from typing import Any

from data_intelligence.machine_learning.base import (MachineLearningError,
                                                     Model)


class KNearestNeighborsModel(Model):
    """Classifies by majority vote among the k nearest examples."""

    def fit(self, x_rows: list[list[float]],
            y_values: list[Any]) -> "KNearestNeighborsModel":
        if len(x_rows) != len(y_values) or not x_rows:
            raise MachineLearningError("X and y must have the same length")
        self.examples = list(zip(x_rows, y_values))
        self.classes = sorted({label for _, label in self.examples})
        return self

    def predict(self, x_rows: list[list[float]]) -> list[Any]:
        labels, _ = self.predict_with_confidence(x_rows)
        return labels

    def predict_with_confidence(self,
                                x_rows: list[list[float]]) -> tuple[list[Any],
                                                                    list[float]]:
        """Returns (labels, confidences) where confidence is the share of
        agreeing neighbours among the k nearest."""
        if not hasattr(self, "examples"):
            raise MachineLearningError("model not fitted")
        k = max(1, min(int(self.params.get("k", 3)), len(self.examples)))
        labels: list[Any] = []
        confidences: list[float] = []
        for row in x_rows:
            ranked = sorted(self.examples,
                            key=lambda example: _distance(row, example[0]))
            votes = ranked[:k]
            counts: dict[Any, int] = {}
            for _, label in votes:
                counts[label] = counts.get(label, 0) + 1
            best = max(counts, key=lambda label: counts[label])
            labels.append(best)
            confidences.append(counts[best] / k)
        return labels, confidences


def _distance(left: list[float], right: list[float]) -> float:
    return sum((a - b) ** 2 for a, b in zip(left, right)) ** 0.5
