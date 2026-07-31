"""Validator for architecture designs."""
from typing import Any

from .models import ArchitectureComponent, Connector


class ArchitectureValidator:
    """Validates architecture designs for consistency and best practices."""

    def validate(self, components: list[ArchitectureComponent],
                 connectors: list[Connector]) -> dict[str, Any]:
        errors = []
        warnings = []

        component_ids = {c.component_id for c in components}

        # Validate connectors reference existing components
        for conn in connectors:
            if conn.source_id not in component_ids:
                errors.append(f"Connector {conn.connector_id} references unknown source {conn.source_id}")
            if conn.target_id not in component_ids:
                errors.append(f"Connector {conn.connector_id} references unknown target {conn.target_id}")

        # Check for components without interfaces
        for comp in components:
            if not comp.interfaces:
                warnings.append(f"Component {comp.name} has no defined interfaces")

        # Check for components without responsibilities
        for comp in components:
            if not comp.responsibilities:
                warnings.append(f"Component {comp.name} has no defined responsibilities")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "components_checked": len(components),
            "connectors_checked": len(connectors),
        }

    def check_best_practices(self, components: list[ArchitectureComponent]) -> dict[str, Any]:
        practices = {
            "single_responsibility": [],
            "high_cohesion": [],
            "loose_coupling": [],
            "interface_defined": [],
        }
        for comp in components:
            if len(comp.responsibilities) <= 3:
                practices["single_responsibility"].append(comp.name)
            if len(comp.interfaces) > 0:
                practices["interface_defined"].append(comp.name)
            if len(comp.dependencies) <= 2:
                practices["loose_coupling"].append(comp.name)
        return practices
