"""Base classes for machine learning."""

from __future__ import annotations

from typing import Any


class MachineLearningError(Exception):
    """Raised when a model cannot be trained or used."""


def prepare(records: list[dict[str, Any]],
            features: list[str],
            label: str | None = None) -> tuple[list[list[float]], list[Any] | None]:
    """Extracts numeric feature vectors (and optional targets) from records."""
    x_rows: list[list[float]] = []
    y_values: list[Any] = []
    for record in records:
        row: list[float] = []
        for feature in features:
            value = record.get(feature)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                row.append(float(value))
            else:
                raise MachineLearningError(
                    f"feature {feature!r} is not numeric: {value!r}")
        x_rows.append(row)
        if label is not None:
            y_values.append(record.get(label))
    return x_rows, (y_values if label is not None else None)


class Model:
    """Base class for machine learning models."""

    def __init__(self, **params: Any) -> None:
        self.params = params

    def fit(self, x_rows: list[list[float]],
            y_values: list[Any]) -> "Model":
        raise NotImplementedError

    def predict(self, x_rows: list[list[float]]) -> list[Any]:
        raise NotImplementedError
