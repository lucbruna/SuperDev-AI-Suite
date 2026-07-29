from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .source_checker import SourceChecker
from .confidence_score import ConfidenceScorer
from .fact_checker import FactChecker


class EngineState(Enum):
    IDLE = "idle"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class EngineConfig:
    min_confidence_threshold: float = 0.5
    require_source_verification: bool = True
    validate_recency: bool = True
    max_recency_days: int = 365
    enable_fact_checking: bool = True


@dataclass
class EngineMetrics:
    total_validations: int = 0
    successful_validations: int = 0
    failed_validations: int = 0
    high_confidence_count: int = 0
    low_confidence_count: int = 0
    sources_checked: int = 0
    facts_verified: int = 0
    average_confidence: float = 0.0


@dataclass
class ValidationResult:
    knowledge_id: str
    confidence_score: float
    source_score: float
    fact_check_status: str
    is_valid: bool
    details: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class ValidationEngine:
    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or EngineConfig()
        self.state = EngineState.IDLE
        self.metrics = EngineMetrics()
        self.source_checker = SourceChecker()
        self.confidence_scorer = ConfidenceScorer()
        self.fact_checker = FactChecker()
        self._history: list[ValidationResult] = []
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        self.state = EngineState.INITIALIZING
        await asyncio.sleep(0.01)
        self.state = EngineState.READY

    async def stop(self) -> None:
        self.state = EngineState.STOPPING
        await asyncio.sleep(0.01)
        self.state = EngineState.IDLE

    async def validate(self, knowledge_id: str, content: str, source_url: str) -> ValidationResult:
        if self.state != EngineState.READY:
            raise RuntimeError(f"Engine not ready, current state: {self.state.value}")

        async with self._lock:
            self.state = EngineState.RUNNING

        try:
            source_result = await self.source_checker.check_source(source_url)
            source_score = source_result["score"]

            if self.config.enable_fact_checking:
                fact_result = await self.fact_checker.check_fact(knowledge_id, content)
                fact_status = fact_result["status"]
            else:
                fact_status = "unchecked"

            confidence = await self.confidence_scorer.calculate_confidence(
                knowledge_id, content, source_score, fact_status
            )

            is_valid = confidence >= self.config.min_confidence_threshold

            result = ValidationResult(
                knowledge_id=knowledge_id,
                confidence_score=confidence,
                source_score=source_score,
                fact_check_status=fact_status,
                is_valid=is_valid,
                details={
                    "source": source_result,
                    "confidence_breakdown": await self.confidence_scorer.get_confidence_breakdown(knowledge_id),
                },
            )

            self.metrics.total_validations += 1
            self.metrics.sources_checked += 1
            if is_valid:
                self.metrics.successful_validations += 1
                self.metrics.high_confidence_count += 1
            else:
                self.metrics.failed_validations += 1
                self.metrics.low_confidence_count += 1
            if fact_status != "unchecked":
                self.metrics.facts_verified += 1
            self.metrics.average_confidence = (
                self.metrics.average_confidence + (confidence - self.metrics.average_confidence)
                / self.metrics.total_validations
            )

            self._history.append(result)
            return result
        except Exception:
            self.metrics.failed_validations += 1
            raise
        finally:
            async with self._lock:
                self.state = EngineState.READY

    async def validate_knowledge(self, knowledge_id: str, content: str, source_url: str) -> ValidationResult:
        return await self.validate(knowledge_id, content, source_url)

    async def validate_source(self, source_url: str) -> dict[str, Any]:
        return await self.source_checker.check_source(source_url)

    async def get_validation_history(self, limit: int = 10) -> list[ValidationResult]:
        return self._history[-limit:]