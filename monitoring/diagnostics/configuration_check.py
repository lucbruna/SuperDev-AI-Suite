from __future__ import annotations

import os
from typing import Any

from .diagnostic_engine import DiagnosticResult


class ConfigurationCheck:
    """Validates application configuration values."""

    @staticmethod
    def check_env_var(name: str, required: bool = True) -> DiagnosticResult:
        value = os.environ.get(name)
        if required and not value:
            return DiagnosticResult(
                check=f"env_{name}",
                status="failed",
                message=f"Required env var {name} is not set",
            )
        if not value:
            return DiagnosticResult(
                check=f"env_{name}",
                status="passed",
                message=f"Env var {name} is not set (optional)",
            )
        return DiagnosticResult(
            check=f"env_{name}",
            status="passed",
            message=f"Env var {name} is set",
            details={"name": name, "length": len(value)},
        )

    @staticmethod
    def check_path(path: str, writable: bool = False) -> DiagnosticResult:
        issues: list[str] = []
        if not os.path.exists(path):
            issues.append("Path does not exist")
        elif not os.access(path, os.R_OK):
            issues.append("Path is not readable")
        elif writable and not os.access(path, os.W_OK):
            issues.append("Path is not writable")

        if issues:
            return DiagnosticResult(
                check=f"path_{path}",
                status="failed",
                message="; ".join(issues),
                details={"path": path},
            )
        return DiagnosticResult(
            check=f"path_{path}",
            status="passed",
            message=f"Path exists and is accessible",
            details={"path": path, "writable": writable},
        )

    @staticmethod
    def check_numeric_range(name: str, value: float, min_val: float, max_val: float) -> DiagnosticResult:
        if value < min_val:
            return DiagnosticResult(
                check=f"config_{name}",
                status="failed",
                message=f"{name}={value} is below minimum {min_val}",
            )
        if value > max_val:
            return DiagnosticResult(
                check=f"config_{name}",
                status="failed",
                message=f"{name}={value} exceeds maximum {max_val}",
            )
        return DiagnosticResult(
            check=f"config_{name}",
            status="passed",
            message=f"{name}={value} is within range [{min_val}, {max_val}]",
            details={"value": value, "min": min_val, "max": max_val},
        )
