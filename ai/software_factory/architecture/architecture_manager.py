"""Manager for architecture lifecycle and persistence."""
from datetime import datetime
from typing import Any

from .models import (
    ArchitectureComponent,
    ArchitectureDecision,
    ArchitecturePattern,
    ArchitectureView,
    Connector,
    DesignConstraint,
)


class ArchitectureManager:
    """Manages architecture versions, decisions, and constraints."""

    def __init__(self):
        self._components: dict[str, ArchitectureComponent] = {}
        self._connectors: dict[str, Connector] = {}
        self._patterns: dict[str, ArchitecturePattern] = {}
        self._views: dict[str, ArchitectureView] = {}
        self._decisions: list[ArchitectureDecision] = []
        self._constraints: list[DesignConstraint] = []
        self._versions: list[dict[str, Any]] = []

    def save_snapshot(self, version_name: str) -> str:
        snapshot = {
            "version": version_name,
            "timestamp": datetime.utcnow().isoformat(),
            "components_count": len(self._components),
            "connectors_count": len(self._connectors),
        }
        self._versions.append(snapshot)
        return version_name

    def add_constraint(self, constraint: DesignConstraint) -> None:
        self._constraints.append(constraint)

    def get_constraints(self) -> list[DesignConstraint]:
        return list(self._constraints)

    def get_version_history(self) -> list[dict[str, Any]]:
        return list(self._versions)

    def add_decision(self, decision: ArchitectureDecision) -> None:
        self._decisions.append(decision)

    def get_decisions(self) -> list[ArchitectureDecision]:
        return list(self._decisions)

    def get_summary(self) -> dict[str, Any]:
        return {
            "components": len(self._components),
            "connectors": len(self._connectors),
            "patterns": len(self._patterns),
            "views": len(self._views),
            "decisions": len(self._decisions),
            "constraints": len(self._constraints),
            "versions": len(self._versions),
        }
