from __future__ import annotations

import json
import logging
import os
from typing import Any

from .workflow_models import WorkflowDefinition


class WorkflowRepository:
    """Persistent storage for workflow definitions."""

    def __init__(self, storage_path: str = "workflows.json") -> None:
        self._storage_path = storage_path
        self._log = logging.getLogger("superdev.workflow.repository")

    def save(self, definition: WorkflowDefinition) -> None:
        data = self._load_all()
        data[definition.id] = {
            "id": definition.id,
            "name": definition.name,
            "version": definition.version,
            "description": definition.description,
            "steps": [
                {
                    "id": s.id,
                    "name": s.name,
                    "action": s.action,
                    "depends_on": s.depends_on,
                    "max_retries": s.max_retries,
                    "timeout": s.timeout,
                }
                for s in definition.steps
            ],
            "status": definition.status.value,
            "tags": definition.tags,
            "created_at": definition.created_at,
            "updated_at": definition.updated_at,
        }
        self._write_all(data)

    def load(self, workflow_id: str) -> WorkflowDefinition | None:
        data = self._load_all()
        raw = data.get(workflow_id)
        if not raw:
            return None
        from .workflow_factory import WorkflowFactory
        return WorkflowFactory().from_dict(raw)

    def delete(self, workflow_id: str) -> bool:
        data = self._load_all()
        if workflow_id in data:
            del data[workflow_id]
            self._write_all(data)
            return True
        return False

    def list_ids(self) -> list[str]:
        return list(self._load_all().keys())

    def _load_all(self) -> dict[str, Any]:
        try:
            with open(self._storage_path, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _write_all(self, data: dict[str, Any]) -> None:
        with open(self._storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
