from __future__ import annotations

import time
from typing import Any

from ..data_models import DataSourceType
from .collector import BaseCollector


class ProjectCollector(BaseCollector):
    """Collector for project data.

    Collects project snapshots (status, tasks, errors, costs) pushed via
    :meth:`add_project` or pulled from an external callable (``source`` in
    config) that returns an iterable of dicts.
    """

    def __init__(
        self,
        name: str,
        engine: Any | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(name, engine, config)
        self._projects: list[dict[str, Any]] = []

    def get_source_type(self) -> DataSourceType:
        return DataSourceType.PROJECT

    def add_project(
        self,
        project: str,
        status: str = "active",
        tasks_completed: int = 0,
        tasks_total: int = 0,
        errors: int = 0,
        cost: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        snapshot = {
            "project": project,
            "status": status,
            "tasks_completed": tasks_completed,
            "tasks_total": tasks_total,
            "errors": errors,
            "cost": cost,
            "timestamp": time.time(),
        }
        snapshot.update(metadata or {})
        self._projects.append(snapshot)
        return snapshot

    async def collect(self, config: dict[str, Any] | None = None) -> Any:
        config = config or {}
        rows: list[dict[str, Any]] = []

        source = config.get("source") or self.config.get("source")
        if callable(source):
            for item in source():
                if isinstance(item, dict):
                    rows.append(item)
        else:
            projects = list(self._projects)
            if config.get("clear", True):
                self._projects.clear()
            rows = list(projects)

        status_filter = config.get("status") or self.config.get("status")
        if status_filter:
            rows = [row for row in rows if row.get("status") == status_filter]

        return self._build_batch(rows, metadata={"collector": "project"})


__all__ = ["ProjectCollector"]
