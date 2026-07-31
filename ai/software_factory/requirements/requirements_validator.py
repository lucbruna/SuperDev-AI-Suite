"""Validator for requirements quality and completeness."""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from .models import Requirement, RequirementType, Priority


@dataclass
class ValidationResult:
    """Result of validating a requirement."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.is_valid = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


class RequirementsValidator:
    """Validates requirements for completeness, quality, and consistency."""

    def __init__(self):
        self._rules: List[str] = ["title_required", "description_required", "valid_type", "valid_priority"]

    def validate(self, req: Requirement) -> ValidationResult:
        """Validate a single requirement."""
        result = ValidationResult()

        if not req.title:
            result.add_error("Title is required")
        if not req.description:
            result.add_warning("Description is empty")
        if req.requirement_type not in RequirementType:
            result.add_error(f"Invalid requirement type: {req.requirement_type}")
        if req.priority not in Priority:
            result.add_error(f"Invalid priority: {req.priority}")
        if len(req.title) > 200:
            result.add_warning("Title is very long (>200 chars)")
        if not req.acceptance_criteria:
            result.add_warning("No acceptance criteria defined")
        return result

    def validate_many(self, requirements: List[Requirement]) -> List[ValidationResult]:
        """Validate multiple requirements."""
        return [self.validate(r) for r in requirements]

    def check_completeness(self, req: Requirement) -> Dict[str, Any]:
        """Check how complete a requirement is."""
        fields_check = {
            "has_title": bool(req.title),
            "has_description": bool(req.description),
            "has_acceptance_criteria": bool(req.acceptance_criteria),
            "has_tags": bool(req.tags),
            "has_dependencies": bool(req.dependencies),
            "has_author": bool(req.author),
        }
        filled = sum(fields_check.values())
        total = len(fields_check)
        return {
            "completeness": filled / total if total > 0 else 0.0,
            "fields": fields_check,
            "filled": filled,
            "total": total,
        }

    def add_rule(self, rule_name: str) -> None:
        if rule_name not in self._rules:
            self._rules.append(rule_name)

    def get_rules(self) -> List[str]:
        return list(self._rules)
