"""Validation subsystem engine — Knowledge validation and fact-checking."""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field


class ValidationMethod(Enum):
    SOURCE_CHECK = "source_check"
    CROSS_REFERENCE = "cross_reference"
    EXPERT_REVIEW = "expert_review"
    STATISTICAL = "statistical"
    LOGICAL = "logical"


class ValidationResult(Enum):
    VALID = "valid"
    INVALID = "invalid"
    INCONCLUSIVE = "inconclusive"
    OUTDATED = "outdated"


@dataclass
class ValidationCheck:
    check_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    content: str = ""
    method: ValidationMethod = ValidationMethod.SOURCE_CHECK
    result: ValidationResult = ValidationResult.INCONCLUSIVE
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)
    checked_at: datetime = field(default_factory=datetime.now)


@dataclass
class FactCheck:
    fact_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    statement: str = ""
    is_true: Optional[bool] = None
    confidence: float = 0.0
    sources: List[str] = field(default_factory=list)
    explanation: str = ""
    checked_at: datetime = field(default_factory=datetime.now)


@dataclass
class Source:
    source_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    url: str = ""
    reliability: float = 0.5
    last_verified: Optional[datetime] = None
    is_active: bool = True


class ValidationSubEngine:
    def __init__(self, confidence_threshold: float = 0.7):
        self._checks: Dict[str, ValidationCheck] = {}
        self._fact_checks: Dict[str, FactCheck] = {}
        self._sources: Dict[str, Source] = {}
        self._confidence_threshold = confidence_threshold

    def validate_content(self, content: str, method: str = "source_check") -> ValidationCheck:
        vm = ValidationMethod(method) if method in [e.value for e in ValidationMethod] else ValidationMethod.SOURCE_CHECK
        confidence = 0.7 if vm == ValidationMethod.SOURCE_CHECK else 0.5
        result = ValidationResult.VALID if confidence >= self._confidence_threshold else ValidationResult.INCONCLUSIVE
        check = ValidationCheck(content=content, method=vm, result=result, confidence=confidence)
        self._checks[check.check_id] = check
        return check

    def get_check(self, check_id: str) -> Optional[ValidationCheck]:
        return self._checks.get(check_id)

    def fact_check(self, statement: str) -> FactCheck:
        fc = FactCheck(statement=statement)
        self._fact_checks[fc.fact_id] = fc
        return fc

    def get_fact_check(self, fact_id: str) -> Optional[FactCheck]:
        return self._fact_checks.get(fact_id)

    def add_source(self, name: str, url: str, reliability: float = 0.5) -> Source:
        source = Source(name=name, url=url, reliability=reliability, last_verified=datetime.now())
        self._sources[source.source_id] = source
        return source

    def get_source(self, source_id: str) -> Optional[Source]:
        return self._sources.get(source_id)

    def check_source_reliability(self, source_id: str) -> float:
        source = self._sources.get(source_id)
        return source.reliability if source else 0.0

    def cross_validate(self, content: str, source_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        checks = []
        for check in self._checks.values():
            if content.lower() in check.content.lower() or check.content.lower() in content.lower():
                checks.append(check)
        valid_count = sum(1 for c in checks if c.result == ValidationResult.VALID)
        total = len(checks)
        return {
            "content": content,
            "matching_checks": total,
            "valid": valid_count,
            "confidence": valid_count / total if total > 0 else 0.0,
        }

    def get_validated_content(self) -> List[ValidationCheck]:
        return [c for c in self._checks.values() if c.result == ValidationResult.VALID]

    def get_invalid_content(self) -> List[ValidationCheck]:
        return [c for c in self._checks.values() if c.result == ValidationResult.INVALID]

    def get_stats(self) -> dict:
        checks = list(self._checks.values())
        return {
            "total_checks": len(checks),
            "valid": len([c for c in checks if c.result == ValidationResult.VALID]),
            "invalid": len([c for c in checks if c.result == ValidationResult.INVALID]),
            "inconclusive": len([c for c in checks if c.result == ValidationResult.INCONCLUSIVE]),
            "fact_checks": len(self._fact_checks),
            "sources": len(self._sources),
        }
