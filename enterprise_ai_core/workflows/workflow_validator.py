"""
Workflow Validator - Validates workflow definitions
"""

from typing import Any, Dict, List


class WorkflowValidator:
    """Validates workflow definitions"""

    def validate(self, workflow: Dict) -> List[str]:
        errors = []
        if not workflow.get("name"):
            errors.append("Workflow must have a name")
        if not workflow.get("steps"):
            errors.append("Workflow must have at least one step")
        return errors