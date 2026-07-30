from __future__ import annotations

import json
from typing import Any

from .workflow_definition import WorkflowDefinition
from .parser import DefinitionParser


class WorkflowImporter:
    """Imports workflow definitions from files."""

    @staticmethod
    def import_json(filepath: str) -> WorkflowDefinition:
        with open(filepath, encoding="utf-8") as f:
            return DefinitionParser.from_json(f.read())

    @staticmethod
    def import_yaml(filepath: str) -> WorkflowDefinition:
        with open(filepath, encoding="utf-8") as f:
            return DefinitionParser.from_yaml(f.read())

    @staticmethod
    def import_dict(data: dict[str, Any]) -> WorkflowDefinition:
        return DefinitionParser.from_dict(data)
