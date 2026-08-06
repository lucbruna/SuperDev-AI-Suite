"""Validator for twin model integrity."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.digital_twin.config.constants import ENTITY_TYPES, RELATION_KINDS
from modules.digital_twin.twin_engine.digital_twin_builder import TwinModel

SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"


@dataclass(slots=True)
class ValidationIssue:
    """A single issue found during twin validation."""

    severity: str
    message: str
    entity_id: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "message": self.message,
            "entity_id": self.entity_id,
        }


@dataclass(slots=True)
class ValidationReport:
    """Aggregate validation outcome."""

    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return all(i.severity != SEVERITY_ERROR for i in self.issues)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == SEVERITY_ERROR]

    def to_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "issues": [i.to_dict() for i in self.issues],
        }


class TwinValidator:
    """Checks entity types, relationship endpoints and reference integrity."""

    def __init__(
        self,
        entity_types: tuple[str, ...] = ENTITY_TYPES,
        relation_kinds: tuple[str, ...] = RELATION_KINDS,
    ) -> None:
        self._entity_types = entity_types
        self._relation_kinds = relation_kinds

    def validate(self, model: TwinModel) -> ValidationReport:
        report = ValidationReport()
        ids = set(model.entities)

        for entity_id, entity in model.entities.items():
            etype = entity.get("type", "")
            if etype not in self._entity_types:
                report.issues.append(
                    ValidationIssue(SEVERITY_ERROR, f"unknown entity type: {etype}", entity_id)
                )
            if not entity.get("name"):
                report.issues.append(
                    ValidationIssue(SEVERITY_WARNING, "entity has no name", entity_id)
                )

        for rel in model.relationships:
            source = rel.get("source", "")
            target = rel.get("target", "")
            kind = rel.get("kind", "")
            if source not in ids:
                report.issues.append(
                    ValidationIssue(SEVERITY_ERROR, f"dangling relationship source: {source}")
                )
            if target not in ids:
                report.issues.append(
                    ValidationIssue(SEVERITY_ERROR, f"dangling relationship target: {target}")
                )
            if kind not in self._relation_kinds:
                report.issues.append(
                    ValidationIssue(SEVERITY_WARNING, f"unknown relationship kind: {kind}")
                )
        return report
