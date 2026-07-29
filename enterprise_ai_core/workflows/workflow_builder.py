"""
Workflow Builder - Builds workflows from definitions
"""

from typing import Any, Dict, List
from uuid import UUID


class WorkflowBuilder:
    """Builds workflows from definitions"""

    def build(self, definition: Dict) -> Dict:
        return {
            "name": definition.get("name", "workflow"),
            "description": definition.get("description", ""),
            "version": definition.get("version", "1.0.0"),
            "steps": definition.get("steps", []),
        }

    def validate(self, workflow: Dict) -> List[str]:
        errors = []
        if not workflow.get("name"):
            errors.append("Workflow must have a name")
        if not workflow.get("steps"):
            errors.append("Workflow must have at least one step")
        return errors