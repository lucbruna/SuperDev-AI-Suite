"""Core engine for architecture design and analysis."""
from typing import List, Dict, Any, Optional
from .models import (
    ArchitectureComponent, Connector, ArchitecturePattern,
    ArchitectureView, ArchitectureDecision,
)
from .architecture_designer import ArchitectureDesigner
from .architecture_analyzer import ArchitectureAnalyzer
from .architecture_validator import ArchitectureValidator


class ArchitectureEngine:
    """Central engine coordinating architecture operations."""

    def __init__(self):
        self.designer = ArchitectureDesigner()
        self.analyzer = ArchitectureAnalyzer()
        self.validator = ArchitectureValidator()
        self._components: Dict[str, ArchitectureComponent] = {}
        self._connectors: Dict[str, Connector] = {}
        self._patterns: Dict[str, ArchitecturePattern] = {}
        self._views: Dict[str, ArchitectureView] = {}
        self._decisions: List[ArchitectureDecision] = []

    def add_component(self, component: ArchitectureComponent) -> str:
        self._components[component.component_id] = component
        return component.component_id

    def add_connector(self, connector: Connector) -> str:
        self._connectors[connector.connector_id] = connector
        return connector.connector_id

    def get_component(self, component_id: str) -> Optional[ArchitectureComponent]:
        return self._components.get(component_id)

    def get_connector(self, connector_id: str) -> Optional[Connector]:
        return self._connectors.get(connector_id)

    def analyze_architecture(self) -> Dict[str, Any]:
        return self.analyzer.analyze(
            list(self._components.values()),
            list(self._connectors.values()),
        )

    def validate_architecture(self) -> Dict[str, Any]:
        return self.validator.validate(
            list(self._components.values()),
            list(self._connectors.values()),
        )

    def add_pattern(self, pattern: ArchitecturePattern) -> None:
        self._patterns[pattern.pattern_id] = pattern

    def add_view(self, view: ArchitectureView) -> None:
        self._views[view.view_id] = view

    def add_decision(self, decision: ArchitectureDecision) -> None:
        self._decisions.append(decision)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "components": len(self._components),
            "connectors": len(self._connectors),
            "patterns": len(self._patterns),
            "views": len(self._views),
            "decisions": len(self._decisions),
        }
