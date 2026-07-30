from __future__ import annotations

import json
from typing import Any

from .workflow_definition import WorkflowDefinition


class WorkflowExporter:
    """Exports workflow definitions to files."""

    @staticmethod
    def export_json(definition: WorkflowDefinition, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(definition.to_dict(), f, indent=2, default=str)

    @staticmethod
    def to_dict(definition: WorkflowDefinition) -> dict[str, Any]:
        return definition.to_dict()
