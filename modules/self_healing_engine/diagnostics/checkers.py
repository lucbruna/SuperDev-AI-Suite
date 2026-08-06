"""Deterministic diagnostic checkers for the Self-Healing Engine."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from modules.self_healing_engine.config.constants import (
    CHECK_CONFIGURATION,
    CHECK_CONSISTENCY,
    CHECK_DEPENDENCIES,
    CHECK_INTEGRITY,
    CHECK_PASSED,
    CHECK_WARNING,
    SEV_INFO,
    SEV_WARNING,
)
from modules.self_healing_engine.core.healing_context import HealingContext


@dataclass(slots=True)
class CheckResult:
    """Outcome of a single diagnostic check."""

    kind: str
    name: str
    status: str
    severity: str
    message: str = ""
    details: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "name": self.name,
            "status": self.status,
            "severity": self.severity,
            "message": self.message,
            "details": self.details,
        }


class DiagnosticCheck(ABC):
    """Base class for a deterministic diagnostic check."""

    name: str = "check"
    kind: str = CHECK_CONFIGURATION

    @abstractmethod
    def run(self, ctx: HealingContext) -> CheckResult:
        raise NotImplementedError


class ConfigurationCheck(DiagnosticCheck):
    """Validates that the healing config was resolved with runtime paths."""

    name = "configuration"
    kind = CHECK_CONFIGURATION

    def run(self, ctx: HealingContext) -> CheckResult:
        if not ctx.config.project_root:
            return CheckResult(
                kind=self.kind,
                name=self.name,
                status=CHECK_WARNING,
                severity=SEV_WARNING,
                message="config.resolve() not called; runtime paths unresolved",
                details={"enabled": ctx.config.enabled},
            )
        return CheckResult(
            kind=self.kind,
            name=self.name,
            status=CHECK_PASSED,
            severity=SEV_INFO,
            message="configuration resolved",
            details={
                "name": ctx.config.name,
                "enabled": ctx.config.enabled,
                "data_dir": ctx.config.data_dir,
            },
        )


class RegistryCheck(DiagnosticCheck):
    """Validates that expected components are registered in the context."""

    name = "registry"
    kind = CHECK_CONSISTENCY

    def run(self, ctx: HealingContext) -> CheckResult:
        names = ctx.registry.names()
        if not names:
            return CheckResult(
                kind=self.kind,
                name=self.name,
                status=CHECK_WARNING,
                severity=SEV_WARNING,
                message="no components registered",
            )
        return CheckResult(
            kind=self.kind,
            name=self.name,
            status=CHECK_PASSED,
            severity=SEV_INFO,
            message="components registered",
            details={"names": names},
        )


class MemoryCheck(DiagnosticCheck):
    """Validates that the healing memory has recorded observations."""

    name = "memory"
    kind = CHECK_INTEGRITY

    def run(self, ctx: HealingContext) -> CheckResult:
        entries = len(ctx.memory)
        if entries == 0:
            return CheckResult(
                kind=self.kind,
                name=self.name,
                status=CHECK_WARNING,
                severity=SEV_WARNING,
                message="memory empty",
            )
        return CheckResult(
            kind=self.kind,
            name=self.name,
            status=CHECK_PASSED,
            severity=SEV_INFO,
            message="memory healthy",
            details={"entries": entries},
        )


class DependencyCheck(DiagnosticCheck):
    """Placeholder deterministic dependency check."""

    name = "dependencies"
    kind = CHECK_DEPENDENCIES

    def run(self, ctx: HealingContext) -> CheckResult:
        return CheckResult(
            kind=self.kind,
            name=self.name,
            status=CHECK_PASSED,
            severity=SEV_INFO,
            message="no dependency scan configured",
        )


DEFAULT_CHECKERS: tuple[DiagnosticCheck, ...] = (
    ConfigurationCheck(),
    RegistryCheck(),
    MemoryCheck(),
    DependencyCheck(),
)
