from __future__ import annotations

import statistics
import time
from typing import Any

from ..data_models import MLModel, ModelStatus, ModelVersion, TrainingRun


class MLEngine:
    """Machine Learning — model manager, training, validation, evaluation,
    deployment, feature engineering, registry, experimentation."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.machine_learning
        self._models: dict[str, MLModel] = {}
        self._versions: dict[str, list[ModelVersion]] = {}
        self._training_runs: dict[str, TrainingRun] = {}
        self._experiments: dict[str, dict[str, Any]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    # -- model registry ------------------------------------------------------

    def register_model(self, name: str, algorithm: str = "linear_regression") -> MLModel:
        model = MLModel(name=name, algorithm=algorithm)
        self._models[model.model_id] = model
        self.engine.registry.register_model(model)
        return model

    def get_model(self, model_id: str) -> MLModel | None:
        return self._models.get(model_id)

    def list_models(self) -> list[MLModel]:
        return list(self._models.values())

    # -- training ------------------------------------------------------------

    async def train(
        self,
        model_id: str,
        dataset: str,
        hyperparameters: dict[str, Any] | None = None,
    ) -> TrainingRun:
        model = self._models.get(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")

        run = TrainingRun(
            model_id=model_id,
            dataset=dataset,
            hyperparameters=hyperparameters or {},
            status="training",
        )
        self._training_runs[run.run_id] = run
        model.status = ModelStatus.TRAINING
        self.engine.metrics.increment("ml.training_runs")

        # Simple heuristic training loop
        metric_value = self._train_heuristic(dataset, run.hyperparameters)
        run.metrics = {"r2": metric_value, "mae": 1 - metric_value}
        run.status = "completed"
        run.completed_at = time.time()
        model.status = ModelStatus.READY
        model.metrics = dict(run.metrics)
        return run

    def _train_heuristic(self, _dataset: str, hyperparameters: dict[str, Any]) -> float:
        # Placeholder quality score; swappable with a real model backend.
        base = hyperparameters.get("quality", 0.8)
        return float(base)

    # -- versions ------------------------------------------------------------

    def create_version(self, model_id: str, version: str, artifact_path: str = "") -> ModelVersion:
        model = self._models.get(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")
        model_version = ModelVersion(
            model_id=model_id,
            version=version,
            artifact_path=artifact_path,
            metrics=dict(model.metrics),
        )
        self._versions.setdefault(model_id, []).append(model_version)
        model.version = version
        return model_version

    def list_versions(self, model_id: str) -> list[ModelVersion]:
        return self._versions.get(model_id, [])

    # -- deployment ----------------------------------------------------------

    def deploy(self, model_id: str, environment: str = "production") -> bool:
        model = self._models.get(model_id)
        if not model or model.status != ModelStatus.READY:
            return False
        model.status = ModelStatus.DEPLOYED
        self.engine.metrics.increment("ml.deployments", labels={"environment": environment})
        return True

    # -- prediction ----------------------------------------------------------

    def predict(self, model_id: str, features: dict[str, Any]) -> dict[str, Any]:
        model = self._models.get(model_id)
        if not model or model.status not in (ModelStatus.READY, ModelStatus.DEPLOYED):
            raise ValueError(f"Model not ready: {model_id}")

        values = [v for v in features.values() if isinstance(v, (int, float))]
        if not values:
            prediction = 0.0
        elif model.algorithm == "linear_regression":
            prediction = sum(values) / len(values)
        else:
            prediction = statistics.median(values)
        return {"prediction": prediction, "model_id": model_id}

    # -- experimentation -----------------------------------------------------

    def start_experiment(self, name: str, params: dict[str, Any] | None = None) -> str:
        experiment_id = f"exp-{len(self._experiments) + 1}"
        self._experiments[experiment_id] = {
            "name": name,
            "params": params or {},
            "metrics": {},
            "started_at": time.time(),
        }
        return experiment_id

    def log_metric(self, experiment_id: str, name: str, value: float) -> bool:
        experiment = self._experiments.get(experiment_id)
        if not experiment:
            return False
        experiment["metrics"][name] = value
        return True

    # -- feature engineering -------------------------------------------------

    @staticmethod
    def scale(values: list[float]) -> list[float]:
        if not values:
            return []
        minimum, maximum = min(values), max(values)
        if maximum == minimum:
            return [0.0] * len(values)
        return [(v - minimum) / (maximum - minimum) for v in values]

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "models": len(self._models),
            "versions": sum(len(v) for v in self._versions.values()),
            "training_runs": len(self._training_runs),
            "experiments": len(self._experiments),
        }


__all__ = ["MLEngine"]
