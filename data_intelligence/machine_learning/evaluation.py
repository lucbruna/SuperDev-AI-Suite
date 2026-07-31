"""Model evaluation metrics (regression and classification)."""

from __future__ import annotations

from typing import Any


def evaluate_regression(y_true: list[float],
                        y_pred: list[float]) -> dict[str, float]:
    """Computes MAE, MSE, RMSE and R2 for numeric predictions."""
    if len(y_true) != len(y_pred) or not y_true:
        raise ValueError("empty or mismatched predictions")
    errors = [actual - predicted for actual, predicted in zip(y_true, y_pred)]
    mae = sum(abs(error) for error in errors) / len(errors)
    mse = sum(error ** 2 for error in errors) / len(errors)
    mean = sum(y_true) / len(y_true)
    total_variance = sum((actual - mean) ** 2 for actual in y_true)
    residual = sum(error ** 2 for error in errors)
    r2 = 1.0 - residual / total_variance if total_variance else 0.0
    return {"mae": mae, "mse": mse, "rmse": mse ** 0.5, "r2": r2}


def evaluate_classification(y_true: list[Any],
                            y_pred: list[Any]) -> dict[str, float]:
    """Computes accuracy and per-class precision/recall/F1."""
    if len(y_true) != len(y_pred) or not y_true:
        raise ValueError("empty or mismatched predictions")
    pairs = list(zip(y_true, y_pred))
    correct = sum(1 for actual, predicted in pairs if actual == predicted)
    metrics: dict[str, float] = {"accuracy": correct / len(pairs)}
    for class_label in sorted({actual for actual, _ in pairs}):
        true_positive = sum(1 for a, p in pairs
                            if a == class_label and p == class_label)
        false_positive = sum(1 for a, p in pairs
                             if a != class_label and p == class_label)
        false_negative = sum(1 for a, p in pairs
                             if a == class_label and p != class_label)
        precision = (true_positive / (true_positive + false_positive)
                     if true_positive + false_positive else 0.0)
        recall = (true_positive / (true_positive + false_negative)
                  if true_positive + false_negative else 0.0)
        f1 = (2 * precision * recall / (precision + recall)
              if precision + recall else 0.0)
        metrics[f"precision.{class_label}"] = precision
        metrics[f"recall.{class_label}"] = recall
        metrics[f"f1.{class_label}"] = f1
    return metrics
