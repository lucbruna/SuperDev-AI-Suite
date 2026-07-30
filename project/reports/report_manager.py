from __future__ import annotations

import logging
import uuid
from typing import Any


class Report:
    """Represents a project report."""

    def __init__(self, title: str, project_id: str) -> None:
        self.id = str(uuid.uuid4())
        self.title = title
        self.project_id = project_id
        self.data: dict[str, Any] = {}


class ReportManager:
    """Manages project reports."""

    def __init__(self) -> None:
        self._reports: dict[str, Report] = {}
        self._log = logging.getLogger("superdev.project.reports")

    def create(self, title: str, project_id: str) -> Report:
        r = Report(title=title, project_id=project_id)
        self._reports[r.id] = r
        return r

    def get(self, report_id: str) -> Report | None:
        return self._reports.get(report_id)

    def list_by_project(self, project_id: str) -> list[Report]:
        return [r for r in self._reports.values() if r.project_id == project_id]
