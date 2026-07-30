from __future__ import annotations

from typing import Any

from .api_docs import APIDocs
from .architecture_docs import ArchitectureDocs
from .changelog_generator import ChangelogGenerator
from .markdown_generator import MarkdownGenerator
from .openapi_generator import OpenAPIGenerator
from .release_notes import ReleaseNotes
from .uml_generator import UMLGenerator
from .user_manual import UserManual


class DocumentationEngine:
    """Central orchestrator for documentation generation workflows."""

    def __init__(self) -> None:
        self._markdown = MarkdownGenerator()
        self._openapi = OpenAPIGenerator()
        self._uml = UMLGenerator()
        self._changelog = ChangelogGenerator()
        self._release_notes = ReleaseNotes()
        self._architecture = ArchitectureDocs()
        self._api_docs = APIDocs()
        self._user_manual = UserManual()

    @property
    def markdown(self) -> MarkdownGenerator:
        return self._markdown

    @property
    def openapi(self) -> OpenAPIGenerator:
        return self._openapi

    @property
    def uml(self) -> UMLGenerator:
        return self._uml

    @property
    def changelog(self) -> ChangelogGenerator:
        return self._changelog

    @property
    def release_notes(self) -> ReleaseNotes:
        return self._release_notes

    @property
    def architecture(self) -> ArchitectureDocs:
        return self._architecture

    @property
    def api_docs(self) -> APIDocs:
        return self._api_docs

    @property
    def user_manual(self) -> UserManual:
        return self._user_manual

    def run_documentation(self, target: dict[str, Any]) -> dict[str, Any]:
        content = target.get("content", "")
        result = self._markdown.generate_markdown(content)
        return {"status": "generated", "documents": 1, "preview": result[:50] + "..." if len(result) > 50 else result}

    def get_status(self) -> dict[str, Any]:
        return {
            "sections": self._markdown.section_count,
            "openapi_endpoints": self._openapi.endpoint_count,
            "uml_classes": self._uml.class_count,
            "changelog_entries": self._changelog.entry_count,
            "releases": self._release_notes.release_count,
            "components": self._architecture.component_count,
            "api_endpoints": self._api_docs.endpoint_count,
            "manual_sections": self._user_manual.section_count,
        }

    def to_dict(self) -> dict[str, Any]:
        return {"agent": "documentation_agent", "status": self.get_status()}
