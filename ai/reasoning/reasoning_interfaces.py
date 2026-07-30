from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .reasoning_context import ReasoningContext
from .reasoning_models import ReasoningResult


class IReasoningEngine(ABC):
    """Interface for the reasoning engine."""

    @abstractmethod
    async def reason(self, context: ReasoningContext) -> ReasoningResult: ...


class IReasoningMemory(ABC):
    """Interface for reasoning memory storage."""

    @abstractmethod
    async def store(self, key: str, value: Any) -> None: ...

    @abstractmethod
    async def retrieve(self, key: str) -> Any: ...

    @abstractmethod
    async def forget(self, key: str) -> bool: ...


class IHypothesisGenerator(ABC):
    """Interface for hypothesis generation."""

    @abstractmethod
    async def generate(self, context: ReasoningContext) -> str: ...


class IHypothesisEvaluator(ABC):
    """Interface for hypothesis evaluation."""

    @abstractmethod
    async def evaluate(self, hypothesis: str, context: ReasoningContext) -> dict[str, Any]: ...
