from __future__ import annotations

import random
import statistics
from collections.abc import Callable
from typing import Any


class ModelTrainer:
    """Training toolkit for the ML subsystem.

    Provides model-agnostic training utilities used by the MLEngine: dataset
    splits, k-fold cross-validation, standard evaluation metrics (R², MAE,
    RMSE, MAPE) and classification confusion matrices. All methods are
    stdlib-only and deterministic when a seed is provided.
    """

    def __init__(self, engine: Any | None = None, seed: int | None = None) -> None:
        self.engine = engine
        self.seed = seed
        self._eval_history: list[dict[str, Any]] = []

    # -- splits --------------------------------------------------------------

    def train_test_split(
        self,
        values: list[float],
        ratio: float = 0.8,
    ) -> tuple[list[float], list[float]]:
        """Deterministic (seeded) train/test split of a flat series."""
        if not values:
            return [], []
        ratio = max(0.0, min(1.0, ratio))
        split_at = max(1, int(len(values) * ratio))
        if split_at >= len(values):
            split_at = len(values) - 1
        if split_at < 1:
            split_at = 1
        return values[:split_at], values[split_at:]

    def split_records(
        self,
        records: list[Any],
        ratio: float = 0.8,
    ) -> tuple[list[Any], list[Any]]:
        """Deterministic (seeded) train/test split of a list of records."""
        if not records:
            return [], []
        indices = list(range(len(records)))
        if self.seed is not None:
            random.Random(self.seed).shuffle(indices)
        split_at = max(1, int(len(indices) * ratio))
        return [records[i] for i in indices[:split_at]], [records[i] for i in indices[split_at:]]

    # -- cross-validation ----------------------------------------------------

    def k_fold_indices(
        self,
        n: int,
        folds: int = 5,
    ) -> list[tuple[list[int], list[int]]]:
        """Yield (train_indices, test_indices) tuples for k-fold CV."""
        if n <= 0 or folds <= 1:
            return [(list(range(n)), [])]
        indices = list(range(n))
        if self.seed is not None:
            random.Random(self.seed).shuffle(indices)
        folds_out: list[tuple[list[int], list[int]]] = []
        fold_size = n // folds
        for fold in range(folds):
            start = fold * fold_size
            end = n if fold == folds - 1 else (fold + 1) * fold_size
            test = indices[start:end]
            train = [i for i in indices if i not in test]
            folds_out.append((train, test))
        return folds_out

    def cross_validate(
        self,
        xs: list[float],
        ys: list[float],
        fit_predict: Callable[[list[float], list[float], list[float]], list[float]],
        folds: int = 5,
    ) -> dict[str, Any]:
        """Run k-fold CV. ``fit_predict(train_x, train_y, test_x) -> predictions``."""
        if len(xs) != len(ys) or len(xs) == 0:
            return {"folds": 0, "mean_r2": 0.0, "mean_mae": 0.0, "fold_scores": []}
        fold_scores: list[dict[str, Any]] = []
        for train_idx, test_idx in self.k_fold_indices(len(xs), folds):
            if not test_idx:
                continue
            train_x = [xs[i] for i in train_idx]
            train_y = [ys[i] for i in train_idx]
            test_x = [xs[i] for i in test_idx]
            test_y = [ys[i] for i in test_idx]
            predictions = fit_predict(train_x, train_y, test_x)
            r2 = self.r2(test_y, predictions)
            mae = self.mae(test_y, predictions)
            fold_scores.append({"r2": round(r2, 4), "mae": round(mae, 4)})

        if not fold_scores:
            return {"folds": 0, "mean_r2": 0.0, "mean_mae": 0.0, "fold_scores": []}
        result = {
            "folds": len(fold_scores),
            "mean_r2": round(statistics.mean(f["r2"] for f in fold_scores), 4),
            "mean_mae": round(statistics.mean(f["mae"] for f in fold_scores), 4),
            "fold_scores": fold_scores,
        }
        self._eval_history.append({"kind": "cross_validate", **result})
        if self.engine is not None:
            self.engine.metrics.increment("ml.cross_validations")
        return result

    # -- regression metrics --------------------------------------------------

    @staticmethod
    def r2(actual: list[float], predicted: list[float]) -> float:
        """Coefficient of determination (1.0 = perfect fit)."""
        if not actual or len(actual) != len(predicted):
            return 0.0
        mean = statistics.mean(actual)
        ss_res = sum((a - p) ** 2 for a, p in zip(actual, predicted, strict=False))
        ss_tot = sum((a - mean) ** 2 for a in actual)
        if ss_tot == 0:
            return 1.0 if ss_res == 0 else 0.0
        return round(1 - ss_res / ss_tot, 4)

    @staticmethod
    def mae(actual: list[float], predicted: list[float]) -> float:
        """Mean absolute error."""
        if not actual or len(actual) != len(predicted):
            return 0.0
        return round(sum(abs(a - p) for a, p in zip(actual, predicted, strict=False)) / len(actual), 4)

    @staticmethod
    def rmse(actual: list[float], predicted: list[float]) -> float:
        """Root mean squared error."""
        if not actual or len(actual) != len(predicted):
            return 0.0
        return round(
            (sum((a - p) ** 2 for a, p in zip(actual, predicted, strict=False)) / len(actual)) ** 0.5,
            4,
        )

    @staticmethod
    def mape(actual: list[float], predicted: list[float]) -> float:
        """Mean absolute percentage error (as a fraction)."""
        if not actual or len(actual) != len(predicted):
            return 0.0
        non_zero = [(a, p) for a, p in zip(actual, predicted, strict=False) if a != 0]
        if not non_zero:
            return 0.0
        return round(
            sum(abs(a - p) / abs(a) for a, p in non_zero) / len(non_zero),
            4,
        )

    def evaluate(self, actual: list[float], predicted: list[float]) -> dict[str, Any]:
        """Full regression evaluation: R², MAE, RMSE, MAPE."""
        result = {
            "r2": self.r2(actual, predicted),
            "mae": self.mae(actual, predicted),
            "rmse": self.rmse(actual, predicted),
            "mape": self.mape(actual, predicted),
        }
        self._eval_history.append({"kind": "evaluate", **result})
        if self.engine is not None:
            self.engine.metrics.increment("ml.evaluations")
        return result

    # -- classification ------------------------------------------------------

    @staticmethod
    def confusion_matrix(
        actual: list[Any],
        predicted: list[Any],
        labels: list[Any] | None = None,
    ) -> dict[str, Any]:
        """Confusion matrix for a binary/multiclass classification."""
        unique_labels = labels or sorted({str(a) for a in actual} | {str(p) for p in predicted})
        matrix: dict[str, dict[str, int]] = {label: {other: 0 for other in unique_labels} for label in unique_labels}
        for a, p in zip(actual, predicted, strict=False):
            matrix[str(a)][str(p)] = matrix[str(a)][str(p)] + 1
        return {
            "labels": unique_labels,
            "matrix": matrix,
        }

    def classification_report(
        self,
        actual: list[Any],
        predicted: list[Any],
    ) -> dict[str, Any]:
        """Precision/recall/f1 per label plus overall accuracy."""
        if not actual or len(actual) != len(predicted):
            return {"accuracy": 0.0, "per_label": {}}
        cm = self.confusion_matrix(actual, predicted)
        labels = cm["labels"]
        matrix = cm["matrix"]

        per_label: dict[str, dict[str, float]] = {}
        for label in labels:
            tp = matrix[label][label]
            fp = sum(matrix[other][label] for other in labels if other != label)
            fn = sum(matrix[label][other] for other in labels if other != label)
            precision = tp / (tp + fp) if (tp + fp) else 0.0
            recall = tp / (tp + fn) if (tp + fn) else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
            per_label[label] = {
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
            }

        correct = sum(1 for a, p in zip(actual, predicted, strict=False) if a == p)
        return {
            "accuracy": round(correct / len(actual), 4),
            "per_label": per_label,
        }

    # -- history -------------------------------------------------------------

    def history(self) -> list[dict[str, Any]]:
        return list(self._eval_history)


__all__ = ["ModelTrainer"]
