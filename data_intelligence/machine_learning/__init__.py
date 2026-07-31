"""Machine learning subsystem (Volume 22).

Regression, classification, clustering and collaborative recommendation,
with training, prediction and evaluation pipelines.
"""

from __future__ import annotations

from data_intelligence.machine_learning.base import (MachineLearningError,
                                                     Model, prepare)
from data_intelligence.machine_learning.classification import (
    KNearestNeighborsModel)
from data_intelligence.machine_learning.clustering import KMeansModel
from data_intelligence.machine_learning.engine import (ALGORITHMS,
                                                       MachineLearningEngine)
from data_intelligence.machine_learning.evaluation import (
    evaluate_classification, evaluate_regression)
from data_intelligence.machine_learning.recommendation import (
    CollaborativeFilterModel)
from data_intelligence.machine_learning.regression import (
    LinearRegressionModel)

__all__ = [
    "MachineLearningEngine", "Model", "prepare", "MachineLearningError",
    "LinearRegressionModel", "KNearestNeighborsModel", "KMeansModel",
    "CollaborativeFilterModel", "evaluate_regression",
    "evaluate_classification", "ALGORITHMS",
]
