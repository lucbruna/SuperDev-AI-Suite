"""Exceptions for the Autonomous Developer module.

A single base error with structured context, plus typed subclasses so callers
can catch domain-level failures precisely.
"""
from __future__ import annotations

from typing import Any


class DeveloperError(Exception):
    """Base error for the Autonomous Developer module."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.context = context or {}


class PlanningError(DeveloperError):
    """Raised when a request cannot be decomposed into tasks."""


class GenerationError(DeveloperError):
    """Raised when code generation or file writes fail."""


class ValidationError(DeveloperError):
    """Raised when a generated change fails validation."""


class ExecutionError(DeveloperError):
    """Raised when a command or execution step fails."""


class SecurityError(DeveloperError):
    """Raised when a change or command violates the security rules."""


class PermissionDeniedError(DeveloperError):
    """Raised when the current role cannot perform an operation."""
