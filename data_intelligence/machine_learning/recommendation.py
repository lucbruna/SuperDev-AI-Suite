"""Collaborative recommendation from a user-item rating matrix."""

from __future__ import annotations

from typing import Any

from data_intelligence.machine_learning.base import (MachineLearningError,
                                                     Model)


class CollaborativeFilterModel(Model):
    """Recommends items by similarity-weighted ratings from other users."""

    def fit(self, x_rows: Any,
            y_values: list[Any] | None = None) -> "CollaborativeFilterModel":
        self.ratings: dict[str, dict[str, float]] = {}
        if isinstance(x_rows, dict):
            for user, items in x_rows.items():
                self.ratings[str(user)] = {str(item): float(score)
                                           for item, score in items.items()}
        else:
            for record in x_rows:
                user = str(record["user"])
                item = str(record["item"])
                self.ratings.setdefault(user, {})[item] = float(record["score"])
        self.users = sorted(self.ratings)
        return self

    def recommend(self, user: str,
                  k: int = 3) -> list[tuple[str, float]]:
        """Returns the top-k unseen items with predicted scores."""
        if not hasattr(self, "ratings"):
            raise MachineLearningError("model not fitted")
        if user not in self.ratings:
            return []
        known = set(self.ratings[user])
        scores: dict[str, float] = {}
        weights: dict[str, float] = {}
        for other in self.users:
            if other == user:
                continue
            similarity = self._similarity(user, other)
            if similarity <= 0:
                continue
            for item, score in self.ratings[other].items():
                if item in known:
                    continue
                scores[item] = scores.get(item, 0.0) + similarity * score
                weights[item] = weights.get(item, 0.0) + similarity
        ranked = sorted(
            ((item, scores[item] / weights[item])
             for item in scores if weights[item]),
            key=lambda pair: pair[1], reverse=True)
        return ranked[:k]

    def _similarity(self, left: str, right: str) -> float:
        shared = set(self.ratings[left]) & set(self.ratings[right])
        if not shared:
            return 0.0
        dot = sum(self.ratings[left][item] * self.ratings[right][item]
                  for item in shared)
        norm_left = sum(value ** 2
                        for value in self.ratings[left].values()) ** 0.5
        norm_right = sum(value ** 2
                         for value in self.ratings[right].values()) ** 0.5
        return dot / (norm_left * norm_right) if norm_left and norm_right else 0.0
