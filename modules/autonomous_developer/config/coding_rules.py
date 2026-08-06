"""Coding rules — structural guardrails for generated code.

Environment prefix: ``SUPERDEV_AD_RULES_*``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


@dataclass(slots=True)
class CodingRules:
    """Structural constraints applied by the generator and validator."""

    max_function_lines: int = 60
    max_function_parameters: int = 6
    max_class_lines: int = 400
    max_nesting_depth: int = 4
    max_cyclomatic_complexity: int = 10

    require_docstrings: bool = True
    require_type_hints: bool = True
    forbid_global_state: bool = True
    forbid_bare_excepts: bool = True
    prefer_composition: bool = True
    no_relative_imports: bool = True

    @classmethod
    def from_env(cls) -> CodingRules:
        cfg = cls()
        cfg.max_function_lines = _env_int(
            "SUPERDEV_AD_RULES_MAX_FUNCTION_LINES", cfg.max_function_lines
        )
        cfg.max_function_parameters = _env_int(
            "SUPERDEV_AD_RULES_MAX_PARAMS", cfg.max_function_parameters
        )
        cfg.max_nesting_depth = _env_int(
            "SUPERDEV_AD_RULES_MAX_NESTING", cfg.max_nesting_depth
        )
        cfg.max_cyclomatic_complexity = _env_int(
            "SUPERDEV_AD_RULES_COMPLEXITY", cfg.max_cyclomatic_complexity
        )
        cfg.require_docstrings = _env_bool(
            "SUPERDEV_AD_RULES_DOCSTRINGS", cfg.require_docstrings
        )
        cfg.require_type_hints = _env_bool(
            "SUPERDEV_AD_RULES_TYPE_HINTS", cfg.require_type_hints
        )
        return cfg
