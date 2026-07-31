"""Linear regression via least squares (normal equations)."""

from __future__ import annotations

from typing import Any

from data_intelligence.machine_learning.base import (MachineLearningError,
                                                     Model)


class LinearRegressionModel(Model):
    """Multivariate linear regression using closed-form normal equations."""

    def fit(self, x_rows: list[list[float]],
            y_values: list[Any]) -> "LinearRegressionModel":
        if len(x_rows) != len(y_values) or not x_rows:
            raise MachineLearningError("X and y must have the same length")
        design = [[1.0] + list(row) for row in x_rows]
        width = len(design[0])
        transposed = [[design[j][i] for j in range(len(design))]
                      for i in range(width)]
        normal = [[sum(transposed[i][k] * design[k][j]
                       for k in range(len(design))) for j in range(width)]
                  for i in range(width)]
        rhs = [float(sum(transposed[i][k] * y_values[k]
                         for k in range(len(design)))) for i in range(width)]
        self.coefficients = _solve(normal, rhs)
        return self

    def predict(self, x_rows: list[list[float]]) -> list[float]:
        if not hasattr(self, "coefficients"):
            raise MachineLearningError("model not fitted")
        predictions = []
        for row in x_rows:
            value = self.coefficients[0]
            for coef, feature in zip(self.coefficients[1:], row):
                value += coef * feature
            predictions.append(value)
        return predictions


def _solve(matrix: list[list[float]],
           rhs: list[float]) -> list[float]:
    """Gaussian elimination with partial pivoting."""
    size = len(rhs)
    augmented = [matrix[i][:] + [rhs[i]] for i in range(size)]
    for column in range(size):
        pivot = max(range(column, size),
                    key=lambda row: abs(augmented[row][column]))
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        if abs(pivot_value) < 1e-12:
            raise MachineLearningError("singular feature matrix")
        for row in range(column + 1, size):
            factor = augmented[row][column] / pivot_value
            for col in range(column, size + 1):
                augmented[row][col] -= factor * augmented[column][col]
    solution = [0.0] * size
    for i in range(size - 1, -1, -1):
        solution[i] = (augmented[i][size]
                       - sum(augmented[i][j] * solution[j]
                             for j in range(i + 1, size))) / augmented[i][i]
    return solution
