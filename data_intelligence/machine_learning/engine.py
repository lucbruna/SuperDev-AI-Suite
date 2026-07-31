"""Machine learning engine (attached by the facade as ``ml``).

Trains regression, classification, clustering and recommendation models,
runs predictions and evaluates their accuracy.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from data_intelligence.data_events import (DataIntelligenceEventType,
                                           DataIntelligenceEvents)
from data_intelligence.data_logger import get_logger
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.data_models import (ModelRecord, ModelStatus,
                                           PredictionResult)
from data_intelligence.machine_learning.base import (MachineLearningError,
                                                     Model, prepare)
from data_intelligence.machine_learning.classification import (
    KNearestNeighborsModel)
from data_intelligence.machine_learning.clustering import KMeansModel
from data_intelligence.machine_learning.evaluation import (
    evaluate_classification, evaluate_regression)
from data_intelligence.machine_learning.recommendation import (
    CollaborativeFilterModel)
from data_intelligence.machine_learning.regression import (
    LinearRegressionModel)

ALGORITHMS: dict[str, type] = {
    "linear_regression": LinearRegressionModel,
    "knn": KNearestNeighborsModel,
    "kmeans": KMeansModel,
    "collaborative": CollaborativeFilterModel,
}

SUPERVISED = {"linear_regression", "knn"}


class MachineLearningEngine:
    """Coordinates model training, prediction and evaluation."""

    def __init__(self, events: DataIntelligenceEvents,
                 metrics: DataIntelligenceMetrics, config: Any,
                 context: Any) -> None:
        self._log = get_logger()
        self.events = events
        self.metrics = metrics
        self.config = config
        self.context = context
        self.records: dict[str, ModelRecord] = {}
        self.models: dict[str, Any] = {}

    def train(self, model_id: str, name: str, algorithm: str,
              X: Any, y: list[Any] | None = None,
              **params: Any) -> ModelRecord:
        model_cls = ALGORITHMS.get(algorithm)
        if model_cls is None:
            raise MachineLearningError(f"unknown algorithm: {algorithm}")
        model = model_cls(**params)
        if algorithm == "collaborative":
            model.fit(X)
        else:
            model.fit(X, y)
        record = ModelRecord(model_id=model_id, name=name,
                             algorithm=algorithm, params=params)
        self.records[model_id] = record
        self.models[model_id] = model
        self.metrics.increment("ml.trained")
        self.events.publish(DataIntelligenceEventType.MODEL_TRAINED,
                            {"model_id": model_id})
        self._log.info("trained %s model %s (%s)", algorithm, name, model_id)
        return record

    def predict(self, model_id: str, features: dict[str, Any],
                prediction_id: str | None = None) -> PredictionResult:
        record = self.records.get(model_id)
        model = self.models.get(model_id)
        if record is None or model is None:
            raise MachineLearningError(f"unknown model: {model_id}")
        if record.algorithm == "collaborative":
            value = model.recommend(str(features.get("user")),
                                    k=int(features.get("k", 3)))
        elif record.algorithm == "knn":
            row, _ = prepare([features], list(features))
            value = model.predict(row)[0]
        elif record.algorithm == "kmeans":
            row, _ = prepare([features], list(features))
            value = model.predict(row)[0]
        else:
            row, _ = prepare([features], list(features))
            value = model.predict(row)[0]
        result = PredictionResult(
            prediction_id=prediction_id or f"pred-{uuid4().hex[:8]}",
            model_id=model_id, value=value,
            confidence=self._confidence(model, features, record.algorithm),
            features=features)
        self.metrics.increment("ml.predictions")
        self.events.publish(DataIntelligenceEventType.PREDICTION_MADE,
                            {"model_id": model_id})
        return result

    def evaluate(self, model_id: str, X: list[list[float]],
                 y: list[Any]) -> dict[str, float]:
        record = self.records.get(model_id)
        model = self.models.get(model_id)
        if record is None or model is None:
            raise MachineLearningError(f"unknown model: {model_id}")
        if record.algorithm not in SUPERVISED:
            raise MachineLearningError(
                f"evaluation not supported for {record.algorithm}")
        if record.algorithm == "knn":
            metrics = evaluate_classification(y, model.predict(X))
        else:
            metrics = evaluate_regression(y, model.predict(X))
        record.metrics = metrics
        record.status = ModelStatus.EVALUATED
        self.metrics.increment("ml.evaluated")
        return metrics

    def remove(self, model_id: str) -> bool:
        self.models.pop(model_id, None)
        return self.records.pop(model_id, None) is not None

    def stats(self) -> dict[str, Any]:
        return {"models": sorted(self.records),
                "algorithms": sorted({r.algorithm for r in self.records.values()}),
                "evaluated": sum(1 for r in self.records.values()
                                 if r.status == ModelStatus.EVALUATED)}

    def _confidence(self, model: Any, features: dict[str, Any],
                    algorithm: str) -> float:
        if algorithm == "knn":
            row, _ = prepare([features], list(features))
            _, confidences = model.predict_with_confidence(row)
            return confidences[0]
        record = next((r for r in self.records.values() if r.metrics), None)
        if record is not None and record.algorithm == algorithm:
            if "r2" in record.metrics:
                return max(0.0, min(1.0, record.metrics["r2"]))
            if "accuracy" in record.metrics:
                return record.metrics["accuracy"]
        return 0.0
