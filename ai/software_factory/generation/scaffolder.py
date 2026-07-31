"""Scaffolder for creating project structures."""

from typing import Any

from .models import GeneratedFile, TemplateLanguage


class Scaffolder:
    """Creates project scaffolding and boilerplate structures."""

    def __init__(self):
        self._structures: dict[str, dict[str, str]] = {
            "library": {
                "src/__init__.py": '"""Package."""',
                "tests/__init__.py": "",
                "setup.py": "from setuptools import setup\nsetup(name='{{name}}')",
                "README.md": "# {{name}}\n\nA Python library.",
            },
            "api": {
                "app/__init__.py": '"""API application."""',
                "app/routes.py": "# Routes",
                "app/models.py": "# Models",
                "requirements.txt": "fastapi\nuvicorn",
            },
            "cli": {
                "cli/__init__.py": '"""CLI tool."""',
                "cli/commands.py": "# Commands",
                "setup.py": "from setuptools import setup\nsetup(name='{{name}}')",
            },
        }

    def scaffold(self, config: dict[str, Any]) -> list[GeneratedFile]:
        project_type = config.get("project_type", "library")
        project_name = config.get("project_name", "my_project")
        structure = self._structures.get(project_type, self._structures["library"])

        files = []
        for path_template, content_template in structure.items():
            content = content_template.replace("{{name}}", project_name)
            files.append(
                GeneratedFile(
                    path=path_template,
                    content=content,
                    language=TemplateLanguage.PYTHON,
                )
            )
        return files

    def register_structure(self, name: str, structure: dict[str, str]) -> None:
        self._structures[name] = structure

    def get_structure(self, name: str) -> dict[str, str]:
        return self._structures.get(name, {})

    def list_structures(self) -> list[str]:
        return list(self._structures.keys())
