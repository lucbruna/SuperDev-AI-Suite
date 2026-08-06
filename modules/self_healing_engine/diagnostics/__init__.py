"""Diagnostics: health scoring and deterministic checkers."""
from __future__ import annotations

from modules.self_healing_engine.diagnostics.checkers import (
    DEFAULT_CHECKERS,
    CheckResult,
    ConfigurationCheck,
    DependencyCheck,
    DiagnosticCheck,
    MemoryCheck,
    RegistryCheck,
)
from modules.self_healing_engine.diagnostics.health import (
    HealthScore,
    compute_health_score,
)

__all__ = [
    "DEFAULT_CHECKERS",
    "CheckResult",
    "ConfigurationCheck",
    "DependencyCheck",
    "DiagnosticCheck",
    "HealthScore",
    "MemoryCheck",
    "RegistryCheck",
    "compute_health_score",
]
