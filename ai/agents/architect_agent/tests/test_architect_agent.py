from __future__ import annotations

from ..architecture_engine import ArchitectureEngine
from ..architecture_review import ArchitectureReview
from ..component_modeler import ComponentModeler
from ..constraint_validator import ConstraintValidator
from ..dependency_analyzer import DependencyAnalyzer
from ..design_decision import DesignDecision
from ..diagram_generator import DiagramGenerator
from ..architecture_document import ArchitectureDocument
from ..pattern_identifier import PatternIdentifier
from ..technology_selector import TechnologySelector
from ..template_manager import TemplateManager


class TestComponentModeler:
    def test_add_component(self) -> None:
        cm = ComponentModeler()
        result = cm.add_component("API", "Handles HTTP", ["REST"])
        assert result == "API"

    def test_get_component(self) -> None:
        cm = ComponentModeler()
        cm.add_component("API", "Handles HTTP", ["REST"])
        comp = cm.get_component("API")
        assert comp is not None
        assert comp["name"] == "API"

    def test_get_nonexistent(self) -> None:
        cm = ComponentModeler()
        assert cm.get_component("Nonexistent") is None

    def test_remove_component(self) -> None:
        cm = ComponentModeler()
        cm.add_component("API", "Handles HTTP", ["REST"])
        assert cm.remove_component("API") is True
        assert cm.remove_component("API") is False

    def test_list_components(self) -> None:
        cm = ComponentModeler()
        cm.add_component("API", "Handles HTTP", ["REST"])
        assert len(cm.list_components()) == 1

    def test_component_count(self) -> None:
        cm = ComponentModeler()
        assert cm.component_count == 0
        cm.add_component("A", "Resp", [])
        assert cm.component_count == 1

    def test_to_dict(self) -> None:
        cm = ComponentModeler()
        cm.add_component("A", "Resp", [])
        d = cm.to_dict()
        assert "components" in d
        assert "component_count" in d


class TestPatternIdentifier:
    def test_identify_microservices(self) -> None:
        pi = PatternIdentifier()
        results = pi.identify_from_task("build a microservice with events")
        patterns = {r["pattern"] for r in results}
        assert "microservices" in patterns

    def test_identify_event_driven(self) -> None:
        pi = PatternIdentifier()
        results = pi.identify_from_task("event driven system")
        assert any(r["pattern"] == "event_driven" for r in results)

    def test_identify_caching(self) -> None:
        pi = PatternIdentifier()
        results = pi.identify_from_task("add cache layer for performance")
        assert any(r["pattern"] == "caching" for r in results)

    def test_default_pattern(self) -> None:
        pi = PatternIdentifier()
        results = pi.identify_from_task("unrelated task")
        assert len(results) > 0

    def test_known_patterns(self) -> None:
        pi = PatternIdentifier()
        assert len(pi.known_patterns) > 0
        assert "layered" in pi.known_patterns

    def test_to_dict(self) -> None:
        pi = PatternIdentifier()
        d = pi.to_dict()
        assert "known_patterns" in d


class TestDesignDecision:
    def test_record(self) -> None:
        dd = DesignDecision()
        rid = dd.record("ADR-001", "Use Python", "Need language", ["Python", "JS"], "Python", ["Fast", "Safe"])
        assert rid == "ADR-001"

    def test_get(self) -> None:
        dd = DesignDecision()
        dd.record("ADR-001", "Title", "Ctx", ["Opts"], "Dec", ["Cons"])
        assert dd.get("ADR-001") is not None

    def test_get_nonexistent(self) -> None:
        dd = DesignDecision()
        assert dd.get("nonexistent") is None

    def test_list_decisions(self) -> None:
        dd = DesignDecision()
        dd.record("1", "T", "C", ["O"], "D", ["C"])
        assert len(dd.list_decisions()) == 1

    def test_decision_count(self) -> None:
        dd = DesignDecision()
        assert dd.decision_count == 0
        dd.record("1", "T", "C", ["O"], "D", ["C"])
        assert dd.decision_count == 1

    def test_to_dict(self) -> None:
        dd = DesignDecision()
        dd.record("1", "T", "C", ["O"], "D", ["C"])
        d = dd.to_dict()
        assert "decisions" in d


class TestArchitectureReview:
    def test_submit(self) -> None:
        ar = ArchitectureReview()
        rid = ar.submit("R1", "Review API", "Content", ["Alice", "Bob"])
        assert rid == "R1"

    def test_approve(self) -> None:
        ar = ArchitectureReview()
        ar.submit("R1", "Title", "Content", ["Alice"])
        assert ar.approve("R1", "Alice") is True

    def test_reject(self) -> None:
        ar = ArchitectureReview()
        ar.submit("R1", "Title", "Content", ["Alice"])
        assert ar.reject("R1", "Alice", "Bad design") is True

    def test_get_review(self) -> None:
        ar = ArchitectureReview()
        ar.submit("R1", "Title", "Content", ["A"])
        assert ar.get_review("R1") is not None

    def test_pending_count(self) -> None:
        ar = ArchitectureReview()
        assert ar.pending_count == 0
        ar.submit("R1", "T", "C", ["A"])
        assert ar.pending_count == 1

    def test_to_dict(self) -> None:
        ar = ArchitectureReview()
        ar.submit("R1", "T", "C", ["A"])
        d = ar.to_dict()
        assert "pending_count" in d


class TestDependencyAnalyzer:
    def test_add_dependency(self) -> None:
        da = DependencyAnalyzer()
        da.add_dependency("A", "B")
        assert "B" in da.get_dependencies("A")

    def test_remove_dependency(self) -> None:
        da = DependencyAnalyzer()
        da.add_dependency("A", "B")
        assert da.remove_dependency("A", "B") is True

    def test_get_dependents(self) -> None:
        da = DependencyAnalyzer()
        da.add_dependency("A", "C")
        da.add_dependency("B", "C")
        assert "A" in da.get_dependents("C")
        assert "B" in da.get_dependents("C")

    def test_no_cycles(self) -> None:
        da = DependencyAnalyzer()
        da.add_dependency("A", "B")
        da.add_dependency("B", "C")
        assert da.detect_cycles() == []

    def test_cycle_detection(self) -> None:
        da = DependencyAnalyzer()
        da.add_dependency("A", "B")
        da.add_dependency("B", "C")
        da.add_dependency("C", "A")
        cycles = da.detect_cycles()
        assert len(cycles) > 0

    def test_component_count(self) -> None:
        da = DependencyAnalyzer()
        assert da.component_count == 0
        da.add_dependency("A", "B")
        assert da.component_count >= 2

    def test_to_dict(self) -> None:
        da = DependencyAnalyzer()
        da.add_dependency("A", "B")
        d = da.to_dict()
        assert "dependencies" in d


class TestTechnologySelector:
    def test_recommend(self) -> None:
        ts = TechnologySelector()
        results = ts.recommend(["backend", "api"])
        assert len(results) > 0

    def test_recommend_empty(self) -> None:
        ts = TechnologySelector()
        results = ts.recommend(["xyz123nonexistent"])
        assert len(results) == 0

    def test_add_technology(self) -> None:
        ts = TechnologySelector()
        ts.add_technology("Custom", "tools", ["testing"])
        assert ts.get_technology("Custom") is not None

    def test_get_nonexistent(self) -> None:
        ts = TechnologySelector()
        assert ts.get_technology("Nonexistent") is None

    def test_list_by_category(self) -> None:
        ts = TechnologySelector()
        results = ts.list_by_category("database")
        assert len(results) > 0

    def test_to_dict(self) -> None:
        ts = TechnologySelector()
        d = ts.to_dict()
        assert "technologies" in d


class TestConstraintValidator:
    def test_add_constraint(self) -> None:
        cv = ConstraintValidator()
        result = cv.add_constraint("max_components", "Max 5 components", "limit")
        assert result == "max_components"

    def test_validate_no_constraints(self) -> None:
        cv = ConstraintValidator()
        results = cv.validate({"components": []})
        assert len(results) > 0

    def test_validate_passes(self) -> None:
        cv = ConstraintValidator()
        cv.add_constraint("c1", "Allow anything", "general")
        results = cv.validate({"components": [{"name": "A"}]})
        assert any(r["status"] == "passed" for r in results)

    def test_remove_constraint(self) -> None:
        cv = ConstraintValidator()
        cv.add_constraint("c1", "desc", "g")
        assert cv.remove_constraint("c1") is True
        assert cv.remove_constraint("c1") is False

    def test_constraint_count(self) -> None:
        cv = ConstraintValidator()
        assert cv.constraint_count == 0
        cv.add_constraint("c1", "desc", "g")
        assert cv.constraint_count == 1

    def test_to_dict(self) -> None:
        cv = ConstraintValidator()
        cv.add_constraint("c1", "desc", "g")
        d = cv.to_dict()
        assert "constraints" in d


class TestTemplateManager:
    def test_get_template(self) -> None:
        tm = TemplateManager()
        t = tm.get_template("microservices")
        assert t is not None
        assert t["name"] == "microservices"

    def test_get_nonexistent(self) -> None:
        tm = TemplateManager()
        assert tm.get_template("nonexistent") is None

    def test_list_templates(self) -> None:
        tm = TemplateManager()
        assert len(tm.list_templates()) > 0

    def test_add_template(self) -> None:
        tm = TemplateManager()
        tm.add_template("custom", {"components": []})
        assert tm.get_template("custom") is not None

    def test_apply_template(self) -> None:
        tm = TemplateManager()
        result = tm.apply_template("microservices")
        assert "components" in result
        assert "error" not in result

    def test_apply_nonexistent(self) -> None:
        tm = TemplateManager()
        result = tm.apply_template("nonexistent")
        assert "error" in result

    def test_apply_with_customization(self) -> None:
        tm = TemplateManager()
        result = tm.apply_template("layered", {"components": [{"name": "CustomLayer"}]})
        names = [c["name"] for c in result["components"]]
        assert "CustomLayer" in names

    def test_to_dict(self) -> None:
        tm = TemplateManager()
        d = tm.to_dict()
        assert "templates" in d


class TestDiagramGenerator:
    def test_component_diagram(self) -> None:
        dg = DiagramGenerator()
        result = dg.generate_component_diagram([{"name": "API", "responsibility": "Handle HTTP"}])
        assert "API" in result

    def test_component_diagram_empty(self) -> None:
        dg = DiagramGenerator()
        assert "(no components)" in dg.generate_component_diagram([])

    def test_sequence_diagram(self) -> None:
        dg = DiagramGenerator()
        result = dg.generate_sequence_diagram(["Request", "Response"])
        assert "Request" in result
        assert "Response" in result

    def test_sequence_diagram_empty(self) -> None:
        dg = DiagramGenerator()
        assert "(no steps)" in dg.generate_sequence_diagram([])

    def test_flow_diagram(self) -> None:
        dg = DiagramGenerator()
        result = dg.generate_flow_diagram(["A", "B"], [("A", "B")])
        assert "[A]" in result
        assert "[B]" in result

    def test_to_dict(self) -> None:
        dg = DiagramGenerator()
        d = dg.to_dict()
        assert "formats" in d


class TestArchitectureDocument:
    def test_add_section(self) -> None:
        ad = ArchitectureDocument()
        result = ad.add_section("Overview", "This is the overview")
        assert result == "Overview"

    def test_get_section(self) -> None:
        ad = ArchitectureDocument()
        ad.add_section("Overview", "Content")
        assert ad.get_section("Overview") == "Content"

    def test_remove_section(self) -> None:
        ad = ArchitectureDocument()
        ad.add_section("S1", "C")
        assert ad.remove_section("S1") is True
        assert ad.remove_section("S1") is False

    def test_generate_report(self) -> None:
        ad = ArchitectureDocument()
        ad.add_section("Overview", "Content")
        report = ad.generate_report()
        assert "# Architecture Document" in report
        assert "## Overview" in report
        assert "Content" in report

    def test_generate_report_empty(self) -> None:
        ad = ArchitectureDocument()
        report = ad.generate_report()
        assert "no sections" in report

    def test_section_count(self) -> None:
        ad = ArchitectureDocument()
        assert ad.section_count == 0
        ad.add_section("S1", "C")
        assert ad.section_count == 1

    def test_to_dict(self) -> None:
        ad = ArchitectureDocument()
        ad.add_section("S1", "C")
        d = ad.to_dict()
        assert "sections" in d


class TestArchitectureEngine:
    def test_engine_initializes(self) -> None:
        ae = ArchitectureEngine()
        assert ae.component_modeler is not None
        assert ae.pattern_identifier is not None
        assert ae.design_decision is not None
        assert ae.architecture_review is not None
        assert ae.dependency_analyzer is not None
        assert ae.technology_selector is not None
        assert ae.constraint_validator is not None
        assert ae.template_manager is not None
        assert ae.diagram_generator is not None
        assert ae.architecture_document is not None

    def test_design_architecture(self) -> None:
        ae = ArchitectureEngine()
        ae.component_modeler.add_component("API", "HTTP", ["REST"])
        result = ae.design_architecture("build microservice api", ["backend"])
        assert "task" in result
        assert "patterns" in result
        assert "microservices" in {p["pattern"] for p in result["patterns"]}

    def test_design_architecture_no_requirements(self) -> None:
        ae = ArchitectureEngine()
        result = ae.design_architecture("simple task")
        assert "technology_recommendations" in result

    def test_get_status(self) -> None:
        ae = ArchitectureEngine()
        status = ae.get_status()
        assert "components" in status
        assert "patterns" in status
        assert "decisions" in status
        assert "pending_reviews" in status

    def test_to_dict(self) -> None:
        ae = ArchitectureEngine()
        d = ae.to_dict()
        assert "engine" in d
        assert d["engine"] == "architecture_engine"
