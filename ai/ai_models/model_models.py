"""AI Model data models."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ModelStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    LOADING = "loading"
    ERROR = "error"


class InferenceStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AIModel:
    model_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    provider: str = ""
    model_type: str = "llm"
    status: ModelStatus = ModelStatus.ACTIVE
    version: str = ""
    max_tokens: int = 4096
    cost_per_1k_input: float = 0.01
    cost_per_1k_output: float = 0.03
    capabilities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class InferenceRequest:
    request_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    model_id: str = ""
    prompt: str = ""
    max_tokens: int = 1024
    temperature: float = 0.7
    stream: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass
class InferenceResponse:
    response_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    request_id: str = ""
    model_id: str = ""
    content: str = ""
    tokens_used: int = 0
    latency_ms: float = 0.0
    cost: float = 0.0
    status: InferenceStatus = InferenceStatus.COMPLETED


@dataclass
class EvaluationResult:
    model_id: str = ""
    task_type: str = ""
    score: float = 0.0
    metrics: dict[str, float] = field(default_factory=dict)
    evaluated_at: float = field(default_factory=time.time)


@dataclass
class TrainingJob:
    job_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    model_id: str = ""
    dataset_id: str = ""
    status: str = "pending"
    epochs: int = 3
    learning_rate: float = 0.001
    created_at: float = field(default_factory=time.time)
