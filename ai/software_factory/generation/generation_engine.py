"""Core engine for code generation."""
from typing import List, Dict, Any, Optional
from .models import GeneratedFile, Template, GenerationProject
from .code_generator import CodeGenerator
from .template_engine import TemplateEngine
from .scaffolder import Scaffolder


class GenerationEngine:
    """Central engine coordinating code generation operations."""

    def __init__(self):
        self.generator = CodeGenerator()
        self.template_engine = TemplateEngine()
        self.scaffolder = Scaffolder()
        self._projects: Dict[str, GenerationProject] = {}
        self._generated_files: List[GeneratedFile] = []

    def create_project(self, project: GenerationProject) -> str:
        self._projects[project.project_id] = project
        return project.project_id

    def generate_from_template(self, template: Template, variables: Dict[str, Any],
                               output_path: str) -> GeneratedFile:
        content = template.render(variables)
        gf = GeneratedFile(
            path=output_path,
            content=content,
            language=template.language,
            template_used=template.name,
            variables=variables,
        )
        self._generated_files.append(gf)
        return gf

    def generate_batch(self, template: Template, batch_vars: List[Dict[str, Any]],
                       output_dir: str) -> List[GeneratedFile]:
        results = []
        for i, variables in enumerate(batch_vars):
            path = f"{output_dir}/file_{i}.py"
            results.append(self.generate_from_template(template, variables, path))
        return results

    def scaffold_project(self, config: Dict[str, Any]) -> List[GeneratedFile]:
        files = self.scaffolder.scaffold(config)
        self._generated_files.extend(files)
        return files

    def get_generated_files(self) -> List[GeneratedFile]:
        return list(self._generated_files)

    def get_project(self, project_id: str) -> Optional[GenerationProject]:
        return self._projects.get(project_id)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "projects": len(self._projects),
            "generated_files": len(self._generated_files),
            "templates": self.template_engine.count(),
        }
