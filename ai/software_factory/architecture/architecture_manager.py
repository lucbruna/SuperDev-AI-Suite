"""Manager for architecture lifecycle and persistence."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import (
    ArchitectureComponent, Connector, ArchitecturePattern,
    ArchitectureView, ArchitectureDecision, DesignConstraint,
)


class ArchitectureManager:
    """Manages architecture versions, decisions, and constraints."""

    def __init__(self):
        self._components: Dict[str, ArchitectureComponent] = {}
        self._connectors: Dict[str, Connector] = {}
        self._patterns: Dict[str, ArchitecturePattern] = {}
        self._views: Dict[str, ArchitectureView] = {}
        self._decisions: List[ArchitectureDecision] = []
        self._constraints: List[DesignConstraint] = []
        self._versions: List[Dict[str, Any]] = []

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

    def get_constraints(self) -> List[DesignConstraint]:
        return list(self._constraints)

    def get_version_history(self) -> List[Dict[str, Any]]:
        return list(self._versions)

    def add_decision(self, decision: ArchitectureDecision) -> None:
        self._decisions.append(decision)

    def get_decisions(self) -> List[ArchitectureDecision]:
        return list(self._decisions)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "components": len(self._components),
            "connectors": len(self._connectors),
            "patterns": len(self._patterns),
            "views": len(self._views),
            "decisions": len(self._decisions),
            "constraints": len(self._constraints),
            "versions": len(self._versions),
        }
