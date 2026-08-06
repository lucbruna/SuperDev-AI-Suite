"""Deterministic validators for repaired or modified targets."""
from __future__ import annotations

import ast
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from modules.self_healing_engine.config.security_policy import SecurityPolicy
from modules.self_healing_engine.core.healing_context import HealingContext


@dataclass(slots=True)
class ValidationResult:
    """Outcome of validating a single target."""

    name: str
    passed: bool
    message: str = ""
    target: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "target": self.target,
        }


class Validator(ABC):
    """Base class for a deterministic validator."""

    name: str = "validator"

    @abstractmethod
    def validate(
        self, target: str, ctx: HealingContext
    ) -> ValidationResult:
        raise NotImplementedError


class SyntaxValidator(Validator):
    """Validates Python syntax using the ast module."""

    name = "syntax"

    def validate(
        self, target: str, ctx: HealingContext
    ) -> ValidationResult:
        path = Path(target)
        if not target.endswith(".py"):
            return ValidationResult(
                name=self.name,
                passed=True,
                message="unsupported target (not python)",
                target=target,
            )
        if not path.is_file():
            return ValidationResult(
                name=self.name,
                passed=False,
                message="target not found",
                target=target,
            )
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, OSError) as exc:
            return ValidationResult(
                name=self.name,
                passed=False,
                message=str(exc),
                target=target,
            )
        return ValidationResult(
            name=self.name,
            passed=True,
            message="syntax ok",
            target=target,
        )


class DependencyValidator(Validator):
    """Placeholder deterministic dependency validator."""

    name = "dependencies"

    def validate(
        self, target: str, ctx: HealingContext
    ) -> ValidationResult:
        return ValidationResult(
            name=self.name,
            passed=True,
            message="dependency scan not configured",
            target=target,
        )


class SecurityValidator(Validator):
    """Rejects targets containing forbidden patterns or protected paths."""

    name = "security"

    def __init__(self, security_policy: SecurityPolicy | None = None) -> None:
        self._security_policy = security_policy or SecurityPolicy()

    def validate(
        self, target: str, ctx: HealingContext
    ) -> ValidationResult:
        if self._security_policy.is_path_protected(target):
            return ValidationResult(
                name=self.name,
                passed=False,
                message="target path protected",
                target=target,
            )
        path = Path(target)
        if not path.is_file():
            return ValidationResult(
                name=self.name,
                passed=True,
                message="target not found",
                target=target,
            )
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            return ValidationResult(
                name=self.name,
                passed=False,
                message=str(exc),
                target=target,
            )
        for index, line in enumerate(lines, start=1):
            if self._security_policy.contains_forbidden_pattern(line):
                return ValidationResult(
                    name=self.name,
                    passed=False,
                    message=f"forbidden pattern on line {index}",
                    target=target,
                )
        return ValidationResult(
            name=self.name,
            passed=True,
            message="no security issues",
            target=target,
        )


class ValidatorRunner:
    """Runs a set of validators over a target and reports the summary."""

    def __init__(self, validators: Sequence[Validator] | None = None) -> None:
        self._validators: tuple[Validator, ...] = tuple(
            validators
            if validators is not None
            else (SyntaxValidator(), DependencyValidator(), SecurityValidator())
        )

    def run(
        self,
        target: str,
        ctx: HealingContext,
        validators: Sequence[Validator] | None = None,
    ) -> list[ValidationResult]:
        selected = tuple(validators) if validators is not None else self._validators
        results = [validator.validate(target, ctx) for validator in selected]
        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed
        ctx.publish(
            "validation.completed",
            {"target": target, "passed": passed, "failed": failed},
        )
        return results
