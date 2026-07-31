"""Template engine for managing and rendering templates."""
from typing import List, Dict, Any, Optional
from .models import Template, TemplateVariable


class TemplateEngine:
    """Manages templates and renders them with variables."""

    def __init__(self):
        self._templates: Dict[str, Template] = {}

    def register(self, template: Template) -> None:
        self._templates[template.template_id] = template

    def get(self, template_id: str) -> Optional[Template]:
        return self._templates.get(template_id)

    def get_by_name(self, name: str) -> Optional[Template]:
        for t in self._templates.values():
            if t.name == name:
                return t
        return None

    def render(self, template_id: str, variables: Dict[str, Any]) -> str:
        template = self._templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        return template.render(variables)

    def render_by_name(self, name: str, variables: Dict[str, Any]) -> str:
        template = self.get_by_name(name)
        if not template:
            raise ValueError(f"Template {name} not found")
        return template.render(variables)

    def list_templates(self) -> List[str]:
        return list(self._templates.keys())

    def count(self) -> int:
        return len(self._templates)

    def create_template(self, name: str, content: str,
                        variables: List[TemplateVariable] = None) -> Template:
        template = Template(
            name=name,
            content=content,
            variables=variables or [],
        )
        self._templates[template.template_id] = template
        return template
