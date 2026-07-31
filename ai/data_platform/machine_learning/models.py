"""Machine Learning models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ModelType(Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    FORECASTING = "forecasting"


class ModelStatus(Enum):
    DRAFT = "draft"
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    FAILED = "failed"


class MetricType(Enum):
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1 = "f1"
    MSE = "mse"
    MAE = "mae"


@dataclass
class MLModel:
    model_id: str
    name: str = ""
    model_type: ModelType = ModelType.CLASSIFICATION
    status: ModelStatus = ModelStatus.DRAFT
    dataset: str = ""
    features: list[str] = field(default_factory=list)
    target: str = ""
    hyperparameters: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    trained_at: datetime | None = None


@dataclass
class TrainingJob:
    job_id: str
    model_id: str = ""
    status: ModelStatus = ModelStatus.DRAFT
    train_size: int = 0
    test_size: int = 0
    duration_seconds: float = 0.0
    metrics: dict[str, float] = field(default_factory=dict)
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class Prediction:
    prediction_id: str
    model_id: str = ""
    input_data: dict[str, Any] = field(default_factory=dict)
    output: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ModelVersion:
    version_id: str
    model_id: str = ""
    version: str = ""
    status: ModelStatus = ModelStatus.DRAFT
    metrics: dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
