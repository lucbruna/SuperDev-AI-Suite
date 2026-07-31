"""Base classes for reporting."""

from __future__ import annotations

from typing import Any

from data_intelligence.data_models import ReportFormat, ReportSpec


class ReportingError(Exception):
    """Raised when a report cannot be generated."""


class ReportRenderer:
    """Renders a report payload into the given format."""

    def render(self, report_format: ReportFormat, report: dict[str, Any]) -> str:
        raise NotImplementedError
