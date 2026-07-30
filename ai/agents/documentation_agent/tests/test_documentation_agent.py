from __future__ import annotations

from ..api_docs import APIDocs
from ..architecture_docs import ArchitectureDocs
from ..changelog_generator import ChangelogGenerator
from ..documentation_agent import DocumentationEngine
from ..markdown_generator import MarkdownGenerator
from ..openapi_generator import OpenAPIGenerator
from ..release_notes import ReleaseNotes
from ..uml_generator import UMLGenerator
from ..user_manual import UserManual


class TestMarkdownGenerator:
    def test_add_section(self) -> None:
        mg = MarkdownGenerator()
        mg.add_section("Intro", "Welcome")
        assert mg.section_count == 1

    def test_get_section(self) -> None:
        mg = MarkdownGenerator()
        mg.add_section("Intro", "Welcome")
        assert mg.get_section("Intro") == "Welcome"

    def test_remove_section(self) -> None:
        mg = MarkdownGenerator()
        mg.add_section("Intro", "Welcome")
        assert mg.remove_section("Intro") is True

    def test_generate_markdown(self) -> None:
        mg = MarkdownGenerator()
        result = mg.generate_markdown("Hello")
        assert result == "Hello"

    def test_to_dict(self) -> None:
        mg = MarkdownGenerator()
        mg.add_section("S", "C")
        d = mg.to_dict()
        assert "sections" in d


class TestOpenAPIGenerator:
    def test_add_endpoint(self) -> None:
        og = OpenAPIGenerator()
        og.add_endpoint("GET", "/users", {"summary": "List users"})
        assert og.endpoint_count == 1

    def test_get_endpoint(self) -> None:
        og = OpenAPIGenerator()
        og.add_endpoint("GET", "/users", {})
        assert og.get_endpoint("GET", "/users") is not None

    def test_remove_endpoint(self) -> None:
        og = OpenAPIGenerator()
        og.add_endpoint("GET", "/users", {})
        assert og.remove_endpoint("GET", "/users") is True

    def test_generate_spec(self) -> None:
        og = OpenAPIGenerator()
        og.add_endpoint("GET", "/api", {})
        spec = og.generate_spec()
        assert "GET /api" in spec

    def test_to_dict(self) -> None:
        og = OpenAPIGenerator()
        og.add_endpoint("GET", "/", {})
        d = og.to_dict()
        assert "endpoints" in d


class TestUMLGenerator:
    def test_add_class(self) -> None:
        ug = UMLGenerator()
        ug.add_class("User", ["name", "email"])
        assert ug.class_count == 1

    def test_get_class(self) -> None:
        ug = UMLGenerator()
        ug.add_class("User", [])
        assert ug.get_class("User") is not None

    def test_add_relationship(self) -> None:
        ug = UMLGenerator()
        ug.add_class("A", [])
        ug.add_class("B", [])
        rel = ug.add_relationship("A", "B", "extends")
        assert "A -> B" in rel

    def test_generate_plantuml(self) -> None:
        ug = UMLGenerator()
        ug.add_class("User", ["id"])
        result = ug.generate_plantuml()
        assert "@startuml" in result

    def test_to_dict(self) -> None:
        ug = UMLGenerator()
        ug.add_class("C", [])
        d = ug.to_dict()
        assert "classes" in d


class TestChangelogGenerator:
    def test_add_entry(self) -> None:
        cg = ChangelogGenerator()
        cg.add_entry("1.0.0", "2024-01-01", ["Initial release"])
        assert cg.entry_count == 1

    def test_get_entry(self) -> None:
        cg = ChangelogGenerator()
        cg.add_entry("1.0.0", "2024-01-01", ["Initial release"])
        assert cg.get_entry("1.0.0") is not None

    def test_generate_changelog(self) -> None:
        cg = ChangelogGenerator()
        cg.add_entry("1.0.0", "2024-01-01", ["First"])
        result = cg.generate_changelog()
        assert "1.0.0" in result

    def test_to_dict(self) -> None:
        cg = ChangelogGenerator()
        cg.add_entry("1.0", "d", ["c"])
        d = cg.to_dict()
        assert "entries" in d


class TestReleaseNotes:
    def test_add_release(self) -> None:
        rn = ReleaseNotes()
        rn.add_release("2.0.0", {"features": ["New UI"]})
        assert rn.release_count == 1

    def test_get_release(self) -> None:
        rn = ReleaseNotes()
        rn.add_release("2.0.0", {"features": ["New UI"]})
        assert rn.get_release("2.0.0") is not None

    def test_generate(self) -> None:
        rn = ReleaseNotes()
        rn.add_release("1.0", {"features": ["x"]})
        result = rn.generate()
        assert "1.0" in result

    def test_to_dict(self) -> None:
        rn = ReleaseNotes()
        rn.add_release("1", {"fixes": ["a"]})
        d = rn.to_dict()
        assert "releases" in d


class TestArchitectureDocs:
    def test_add_component(self) -> None:
        ad = ArchitectureDocs()
        ad.add_component("API", "Handles requests")
        assert ad.component_count == 1

    def test_get_component(self) -> None:
        ad = ArchitectureDocs()
        ad.add_component("API", "Handles requests")
        assert ad.get_component("API") == "Handles requests"

    def test_add_context(self) -> None:
        ad = ArchitectureDocs()
        ad.add_context("lang", "Python")
        assert "lang" in ad.to_dict()["context"]

    def test_generate(self) -> None:
        ad = ArchitectureDocs()
        ad.add_component("DB", "Database layer")
        result = ad.generate()
        assert "DB" in result

    def test_to_dict(self) -> None:
        ad = ArchitectureDocs()
        ad.add_component("C", "d")
        d = ad.to_dict()
        assert "components" in d


class TestAPIDocs:
    def test_add_endpoint(self) -> None:
        ad = APIDocs()
        ad.add_endpoint("POST", "/users", [{"name": "name", "type": "string"}])
        assert ad.endpoint_count == 1

    def test_get_endpoint(self) -> None:
        ad = APIDocs()
        ad.add_endpoint("GET", "/x", [])
        assert ad.get_endpoint("GET", "/x") is not None

    def test_generate_docs(self) -> None:
        ad = APIDocs()
        ad.add_endpoint("GET", "/ping", [])
        result = ad.generate_docs()
        assert "GET /ping" in result

    def test_to_dict(self) -> None:
        ad = APIDocs()
        ad.add_endpoint("GET", "/", [])
        d = ad.to_dict()
        assert "endpoints" in d


class TestUserManual:
    def test_add_section(self) -> None:
        um = UserManual()
        um.add_section("Getting Started", "Install instructions")
        assert um.section_count == 1

    def test_get_section(self) -> None:
        um = UserManual()
        um.add_section("Intro", "Text")
        assert um.get_section("Intro") == "Text"

    def test_add_step(self) -> None:
        um = UserManual()
        um.add_step("Setup", "Install package")
        assert len(um._steps["Setup"]) == 1  # type: ignore[attr-defined]

    def test_generate(self) -> None:
        um = UserManual()
        um.add_section("Intro", "Hello")
        result = um.generate()
        assert "Intro" in result

    def test_to_dict(self) -> None:
        um = UserManual()
        um.add_section("S", "C")
        d = um.to_dict()
        assert "sections" in d


class TestDocumentationEngine:
    def test_engine_initializes(self) -> None:
        de = DocumentationEngine()
        assert de.markdown is not None
        assert de.openapi is not None
        assert de.uml is not None
        assert de.changelog is not None
        assert de.release_notes is not None
        assert de.architecture is not None
        assert de.api_docs is not None
        assert de.user_manual is not None

    def test_run_documentation(self) -> None:
        de = DocumentationEngine()
        result = de.run_documentation({"content": "# Test"})
        assert result["status"] == "generated"

    def test_get_status(self) -> None:
        de = DocumentationEngine()
        s = de.get_status()
        assert "sections" in s

    def test_to_dict(self) -> None:
        de = DocumentationEngine()
        d = de.to_dict()
        assert d["agent"] == "documentation_agent"
