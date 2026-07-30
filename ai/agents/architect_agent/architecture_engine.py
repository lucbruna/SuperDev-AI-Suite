from __future__ import annotations

from typing import Any

from .architecture_document import ArchitectureDocument
from .architecture_review import ArchitectureReview
from .component_modeler import ComponentModeler
from .constraint_validator import ConstraintValidator
from .dependency_analyzer import DependencyAnalyzer
from .design_decision import DesignDecision
from .diagram_generator import DiagramGenerator
from .pattern_identifier import PatternIdentifier
from .technology_selector import TechnologySelector
from .template_manager import TemplateManager


class ArchitectureEngine:
    """Central orchestrator for architecture design workflows."""

    def __init__(self) -> None:
        self._component_modeler = ComponentModeler()
        self._pattern_identifier = PatternIdentifier()
        self._design_decision = DesignDecision()
        self._architecture_review = ArchitectureReview()
        self._dependency_analyzer = DependencyAnalyzer()
        self._technology_selector = TechnologySelector()
        self._constraint_validator = ConstraintValidator()
        self._template_manager = TemplateManager()
        self._diagram_generator = DiagramGenerator()
        self._architecture_document = ArchitectureDocument()

    @property
    def component_modeler(self) -> ComponentModeler:
        return self._component_modeler

    @property
    def pattern_identifier(self) -> PatternIdentifier:
        return self._pattern_identifier

    @property
    def design_decision(self) -> DesignDecision:
        return self._design_decision

    @property
    def architecture_review(self) -> ArchitectureReview:
        return self._architecture_review

    @property
    def dependency_analyzer(self) -> DependencyAnalyzer:
        return self._dependency_analyzer

    @property
    def technology_selector(self) -> TechnologySelector:
        return self._technology_selector

    @property
    def constraint_validator(self) -> ConstraintValidator:
        return self._constraint_validator

    @property
    def template_manager(self) -> TemplateManager:
        return self._template_manager

    @property
    def diagram_generator(self) -> DiagramGenerator:
        return self._diagram_generator

    @property
    def architecture_document(self) -> ArchitectureDocument:
        return self._architecture_document

    def design_architecture(
        self,
        task: str,
        requirements: list[str] | None = None,
    ) -> dict[str, Any]:
        patterns = self._pattern_identifier.identify_from_task(task)
        components = list(self._component_modeler.list_components())

        if requirements:
            tech_recommendations = self._technology_selector.recommend(requirements)
        else:
            tech_recommendations = []

        architecture: dict[str, Any] = {
            "task": task,
            "patterns": patterns,
            "components": components if components else self._component_modeler.list_components(),
            "technology_recommendations": tech_recommendations,
            "constraints": [],
            "diagram": self._diagram_generator.generate_component_diagram(
                self._component_modeler.list_components()
            ),
        }

        if self._constraint_validator.constraint_count > 0:
            architecture["constraints"] = self._constraint_validator.validate(architecture)

        return architecture

    def get_status(self) -> dict[str, Any]:
        return {
            "components": self._component_modeler.component_count,
            "patterns": len(self._pattern_identifier.known_patterns),
            "decisions": self._design_decision.decision_count,
            "pending_reviews": self._architecture_review.pending_count,
            "dependencies": self._dependency_analyzer.component_count,
            "constraints": self._constraint_validator.constraint_count,
            "templates": len(self._template_manager.list_templates()),
            "sections": self._architecture_document.section_count,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "architecture_engine",
            "status": self.get_status(),
        }
