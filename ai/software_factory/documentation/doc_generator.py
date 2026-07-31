"""Generic documentation generator."""
from typing import List, Dict, Any
from .models import DocPage, DocSection, DocType


class DocGenerator:
    """Generates documentation pages from specifications."""

    def __init__(self):
        self._templates: Dict[str, str] = {}

    def generate_page(self, title: str, sections: List[Dict[str, Any]],
                      doc_type: DocType = DocType.GUIDE) -> DocPage:
        page = DocPage(title=title, doc_type=doc_type)
        for sec_data in sections:
            section = DocSection(
                title=sec_data.get("title", ""),
                content=sec_data.get("content", ""),
                level=sec_data.get("level", 1),
            )
            page.add_section(section)
        return page

    def generate_from_module(self, module_path: str, description: str = "") -> DocPage:
        sections = [
            {"title": "Overview", "content": description or f"Documentation for {module_path}"},
            {"title": "Usage", "content": f"Import and use the {module_path} module."},
            {"title": "API Reference", "content": "See the API documentation for detailed reference."},
        ]
        return self.generate_page(f"{module_path} Documentation", sections)

    def register_template(self, name: str, template: str) -> None:
        self._templates[name] = template

    def get_template(self, name: str) -> str:
        return self._templates.get(name, "")
