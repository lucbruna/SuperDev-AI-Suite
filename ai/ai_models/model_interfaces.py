"""AI Model interfaces."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ProviderInterface(ABC):
    @abstractmethod
    def complete(self, prompt: str, **kwargs: Any) -> dict[str, Any]: ...
    @abstractmethod
    def stream(self, prompt: str, **kwargs: Any): ...
    @abstractmethod
    def get_models(self) -> list[dict[str, Any]]: ...

class RouterInterface(ABC):
    @abstractmethod
    def select_model(self, task_type: str, requirements: dict[str, Any] = None) -> str: ...
    @abstractmethod
    def route_request(self, request: dict[str, Any]) -> dict[str, Any]: ...

class EvaluationInterface(ABC):
    @abstractmethod
    def evaluate(self, model_id: str, test_cases: list[dict[str, Any]]) -> dict[str, Any]: ...
    @abstractmethod
    def compare(self, model_ids: list[str], test_cases: list[dict[str, Any]]) -> dict[str, Any]: ...

class InferenceInterface(ABC):
    @abstractmethod
    def infer(self, model_id: str, prompt: str, **kwargs: Any) -> dict[str, Any]: ...
    @abstractmethod
    def batch_infer(self, model_id: str, prompts: list[str], **kwargs: Any) -> list[dict[str, Any]]: ...

class TrainingInterface(ABC):
    @abstractmethod
    def train(self, model_id: str, dataset: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]: ...
    @abstractmethod
    def finetune(self, model_id: str, dataset: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]: ...
