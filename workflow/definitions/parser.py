from __future__ import annotations

import json
from typing import Any

from .workflow_definition import WorkflowDefinition


class DefinitionParser:
    """Parses workflow definitions from various formats."""

    @staticmethod
    def from_dict(data: dict[str, Any]) -> WorkflowDefinition:
        import time
        return WorkflowDefinition(
            id=data.get("id", ""),
            name=data.get("name", ""),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            steps=data.get("steps", []),
            triggers=data.get("triggers", []),
            tags=data.get("tags", []),
            variables=data.get("variables", {}),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
        )

    @staticmethod
    def from_json(json_str: str) -> WorkflowDefinition:
        data = json.loads(json_str)
        return DefinitionParser.from_dict(data)

    @staticmethod
    def from_yaml(yaml_str: str) -> WorkflowDefinition:
        import yaml
        data = yaml.safe_load(yaml_str)
        return DefinitionParser.from_dict(data)
