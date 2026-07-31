"""Mapper for linking requirements to implementation artifacts."""
from dataclasses import dataclass, field
from typing import Any

from .models import Requirement


@dataclass
class RequirementMapping:
    """Maps a requirement to implementation artifacts."""
    requirement_id: str = ""
    mapped_artifacts: list[str] = field(default_factory=list)
    coverage: float = 0.0
    notes: str = ""


class RequirementsMapper:
    """Maps requirements to code, tests, and other artifacts."""

    def __init__(self):
        self._mappings: dict[str, RequirementMapping] = {}

    def create_mapping(self, req_id: str) -> RequirementMapping:
        mapping = RequirementMapping(requirement_id=req_id)
        self._mappings[req_id] = mapping
        return mapping

    def get_mapping(self, req_id: str) -> RequirementMapping | None:
        return self._mappings.get(req_id)

    def add_artifact(self, req_id: str, artifact_path: str) -> bool:
        mapping = self._mappings.get(req_id)
        if not mapping:
            mapping = self.create_mapping(req_id)
        if artifact_path not in mapping.mapped_artifacts:
            mapping.mapped_artifacts.append(artifact_path)
        return True

    def compute_coverage(self, requirements: list[Requirement]) -> dict[str, Any]:
        """Compute requirement coverage across mapped artifacts."""
        total = len(requirements)
        covered = sum(1 for r in requirements if r.requirement_id in self._mappings)
        all_artifacts = set()
        for m in self._mappings.values():
            all_artifacts.update(m.mapped_artifacts)
        return {
            "total_requirements": total,
            "covered": covered,
            "coverage_ratio": covered / total if total > 0 else 0.0,
            "unique_artifacts": len(all_artifacts),
        }

    def get_unmapped(self, requirements: list[Requirement]) -> list[Requirement]:
        return [r for r in requirements if r.requirement_id not in self._mappings]

    def get_all_mappings(self) -> list[RequirementMapping]:
        return list(self._mappings.values())
