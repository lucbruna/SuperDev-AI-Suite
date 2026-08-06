"""Quality rules — gates a change must pass before submission.

Environment prefix: ``SUPERDEV_AD_QUALITY_*``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_float(key: str, default: float) -> float:
    raw = os.getenv(key)
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw.strip())
    except ValueError:
        return default


@dataclass(slots=True)
class QualityRules:
    """Quality gates enforced by the validation engine."""

    require_tests: bool = True
    min_test_coverage: float = 0.80
    lint_enabled: bool = True
    type_check_enabled: bool = True
    fail_on_warnings: bool = False

    complexity_threshold: int = 10
    maintainability_threshold: float = 0.70
    duplicate_threshold: float = 0.05

    require_commit_messages: bool = True
    require_review: bool = True
    required_reviewers: int = 1

    @classmethod
    def from_env(cls) -> QualityRules:
        cfg = cls()
        cfg.require_tests = _env_bool(
            "SUPERDEV_AD_QUALITY_REQUIRE_TESTS", cfg.require_tests
        )
        cfg.min_test_coverage = _env_float(
            "SUPERDEV_AD_QUALITY_COVERAGE", cfg.min_test_coverage
        )
        cfg.lint_enabled = _env_bool("SUPERDEV_AD_QUALITY_LINT", cfg.lint_enabled)
        cfg.type_check_enabled = _env_bool(
            "SUPERDEV_AD_QUALITY_TYPE_CHECK", cfg.type_check_enabled
        )
        cfg.require_review = _env_bool(
            "SUPERDEV_AD_QUALITY_REQUIRE_REVIEW", cfg.require_review
        )
        return cfg
