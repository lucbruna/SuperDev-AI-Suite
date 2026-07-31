"""Manager for generator configurations and history."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import Template, GenerationProject


class GeneratorManager:
    """Manages generator configurations, templates, and execution history."""

    def __init__(self):
        self._projects: Dict[str, GenerationProject] = {}
        self._templates: Dict[str, Template] = {}
        self._history: List[Dict[str, Any]] = []

    def register_project(self, project: GenerationProject) -> None:
        self._projects[project.project_id] = project

    def get_project(self, project_id: str) -> Optional[GenerationProject]:
        return self._projects.get(project_id)

    def register_template(self, template: Template) -> None:
        self._templates[template.template_id] = template

    def get_template(self, template_id: str) -> Optional[Template]:
        return self._templates.get(template_id)

    def record_generation(self, project_id: str, template_id: str, output_path: str) -> None:
        self._history.append({
            "project_id": project_id,
            "template_id": template_id,
            "output_path": output_path,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._history)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "projects": len(self._projects),
            "templates": len(self._templates),
            "generations": len(self._history),
        }
