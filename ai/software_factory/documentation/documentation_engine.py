"""Core engine for documentation generation."""
from typing import Any

from .api_doc_generator import ApiDocGenerator
from .changelog_generator import ChangelogGenerator
from .doc_generator import DocGenerator
from .models import ChangelogEntry, DocPage, DocumentationConfig
from .readme_generator import ReadmeGenerator


class DocumentationEngine:
    """Central engine coordinating documentation operations."""

    def __init__(self):
        self.doc_generator = DocGenerator()
        self.api_generator = ApiDocGenerator()
        self.readme_generator = ReadmeGenerator()
        self.changelog_generator = ChangelogGenerator()
        self._pages: dict[str, DocPage] = {}
        self._config = DocumentationConfig()

    def generate_readme(self, project_info: dict[str, Any]) -> str:
        return self.readme_generator.generate(project_info)

    def generate_api_docs(self, endpoints: list[dict[str, Any]]) -> str:
        return self.api_generator.generate(endpoints)

    def generate_changelog(self, entries: list[ChangelogEntry]) -> str:
        return self.changelog_generator.generate(entries)

    def create_page(self, page: DocPage) -> str:
        self._pages[page.page_id] = page
        return page.page_id

    def get_page(self, page_id: str) -> DocPage | None:
        return self._pages.get(page_id)

    def export_all(self) -> dict[str, str]:
        return {pid: page.to_markdown() for pid, page in self._pages.items()}

    def get_stats(self) -> dict[str, Any]:
        return {"pages": len(self._pages)}
