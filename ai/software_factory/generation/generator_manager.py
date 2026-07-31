"""Manager for generator configurations and history."""

from datetime import datetime
from typing import Any

from .models import GenerationProject, Template


class GeneratorManager:
    """Manages generator configurations, templates, and execution history."""

    def __init__(self):
        self._projects: dict[str, GenerationProject] = {}
        self._templates: dict[str, Template] = {}
        self._history: list[dict[str, Any]] = []

    def register_project(self, project: GenerationProject) -> None:
        self._projects[project.project_id] = project

    def get_project(self, project_id: str) -> GenerationProject | None:
        return self._projects.get(project_id)

    def register_template(self, template: Template) -> None:
        self._templates[template.template_id] = template

    def get_template(self, template_id: str) -> Template | None:
        return self._templates.get(template_id)

    def record_generation(self, project_id: str, template_id: str, output_path: str) -> None:
        self._history.append(
            {
                "project_id": project_id,
                "template_id": template_id,
                "output_path": output_path,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def get_history(self) -> list[dict[str, Any]]:
        return list(self._history)

    def get_stats(self) -> dict[str, Any]:
        return {
            "projects": len(self._projects),
            "templates": len(self._templates),
            "generations": len(self._history),
        }
