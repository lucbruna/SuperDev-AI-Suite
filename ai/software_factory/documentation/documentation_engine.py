"""Core engine for documentation generation."""
from typing import List, Dict, Any, Optional
from .models import DocPage, DocumentationConfig, ChangelogEntry
from .doc_generator import DocGenerator
from .api_doc_generator import ApiDocGenerator
from .readme_generator import ReadmeGenerator
from .changelog_generator import ChangelogGenerator


class DocumentationEngine:
    """Central engine coordinating documentation operations."""

    def __init__(self):
        self.doc_generator = DocGenerator()
        self.api_generator = ApiDocGenerator()
        self.readme_generator = ReadmeGenerator()
        self.changelog_generator = ChangelogGenerator()
        self._pages: Dict[str, DocPage] = {}
        self._config = DocumentationConfig()

    def generate_readme(self, project_info: Dict[str, Any]) -> str:
        return self.readme_generator.generate(project_info)

    def generate_api_docs(self, endpoints: List[Dict[str, Any]]) -> str:
        return self.api_generator.generate(endpoints)

    def generate_changelog(self, entries: List[ChangelogEntry]) -> str:
        return self.changelog_generator.generate(entries)

    def create_page(self, page: DocPage) -> str:
        self._pages[page.page_id] = page
        return page.page_id

    def get_page(self, page_id: str) -> Optional[DocPage]:
        return self._pages.get(page_id)

    def export_all(self) -> Dict[str, str]:
        return {pid: page.to_markdown() for pid, page in self._pages.items()}

    def get_stats(self) -> Dict[str, Any]:
        return {"pages": len(self._pages)}
