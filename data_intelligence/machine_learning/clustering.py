"""k-Means clustering."""

from __future__ import annotations

from typing import Any

from data_intelligence.machine_learning.base import (MachineLearningError,
                                                     Model)


class KMeansModel(Model):
    """Groups points into k clusters using Lloyd's algorithm."""

    def fit(self, x_rows: list[list[float]],
            y_values: list[Any] | None = None) -> "KMeansModel":
        k = int(self.params.get("k", 2))
        iterations = int(self.params.get("iterations", 50))
        if not x_rows:
            raise MachineLearningError("cannot cluster an empty dataset")
        if k < 1 or k > len(x_rows):
            raise MachineLearningError(f"invalid k={k} for dataset size")
        centroids = [list(x_rows[i]) for i in range(k)]
        for _ in range(iterations):
            assignments = self._assign(x_rows, centroids)
            new_centroids = []
            for cluster in range(k):
                members = [x_rows[i] for i, assigned in
                           enumerate(assignments) if assigned == cluster]
                if members:
                    width = len(x_rows[0])
                    new_centroids.append(
                        [sum(member[d] for member in members) / len(members)
                         for d in range(width)])
                else:
                    new_centroids.append(list(centroids[cluster]))
            centroids = new_centroids
        self.centroids = centroids
        self.assignments = self._assign(x_rows, centroids)
        self.inertia = sum(_distance2(x_rows[i], centroids[assigned])
                           for i, assigned in enumerate(self.assignments))
        return self

    def predict(self, x_rows: list[list[float]]) -> list[int]:
        if not hasattr(self, "centroids"):
            raise MachineLearningError("model not fitted")
        return self._assign(x_rows, self.centroids)

    @staticmethod
    def _assign(x_rows: list[list[float]],
                centroids: list[list[float]]) -> list[int]:
        return [min(range(len(centroids)),
                    key=lambda c: _distance2(row, centroids[c]))
                for row in x_rows]


def _distance2(left: list[float], right: list[float]) -> float:
    return sum((a - b) ** 2 for a, b in zip(left, right))
