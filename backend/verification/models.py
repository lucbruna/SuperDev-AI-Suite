from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class VerificationStage(StrEnum):
    GENERATE = "generate"
    EXECUTE = "execute"
    TEST = "test"
    REVIEW = "review"
    CORRECT = "correct"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class GenerationResult:
    success: bool = False
    code: str = ""
    language: str = "python"
    explanation: str = ""
    error: str | None = None
    stage: VerificationStage = VerificationStage.GENERATE
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    success: bool = False
    output: str = ""
    error: str | None = None
    exit_code: int = 0
    execution_time: float = 0.0
    stage: VerificationStage = VerificationStage.EXECUTE


@dataclass
class TestResult:
    success: bool = False
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    total: int = 0
    coverage: float = 0.0
    test_output: str = ""
    failures: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    execution_time: float = 0.0
    stage: VerificationStage = VerificationStage.TEST


@dataclass
class ReviewResult:
    success: bool = False
    score: int = 0
    issues: list[dict[str, Any]] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    security_issues: list[dict[str, Any]] = field(default_factory=list)
    performance_issues: list[dict[str, Any]] = field(default_factory=list)
    style_issues: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    stage: VerificationStage = VerificationStage.REVIEW


@dataclass
class CorrectionResult:
    success: bool = False
    corrected_code: str = ""
    changes: list[dict[str, Any]] = field(default_factory=list)
    iterations: int = 0
    error: str | None = None
    stage: VerificationStage = VerificationStage.CORRECT


@dataclass
class VerificationResult:
    task_description: str
    task_id: UUID = field(default_factory=uuid4)
    language: str = "python"
    success: bool = False
    error: str | None = None
    stage: VerificationStage = VerificationStage.GENERATE
    max_iterations: int = 3
    iterations: int = 0
    final_code: str | None = None

    generation: GenerationResult | None = None
    execution: ExecutionResult | None = None
    testing: TestResult | None = None
    review: ReviewResult | None = None
    correction: CorrectionResult | None = None

    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": str(self.task_id),
            "task_description": self.task_description,
            "language": self.language,
            "success": self.success,
            "error": self.error,
            "stage": self.stage.value,
            "iterations": self.iterations,
            "final_code": self.final_code,
            "generation": self.generation.__dict__ if self.generation else None,
            "execution": self.execution.__dict__ if self.execution else None,
            "testing": self.testing.__dict__ if self.testing else None,
            "review": self.review.__dict__ if self.review else None,
            "correction": self.correction.__dict__ if self.correction else None,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class VerificationLoop:
    def __init__(
        self,
        provider: Any = None,
        max_iterations: int = 3,
    ):
        self.provider = provider
        self.max_iterations = max_iterations
