"""Project structure: fases e módulos."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import ProjectStatus
from collaboration.collaboration_protocols import new_id

DEFAULT_PHASES = ["Planejamento", "Desenvolvimento", "Testes", "Deploy"]


class ProjectStructure:
    """Organizes a project into phases and modules."""

    def __init__(self, project_id: str) -> None:
        self.project_id = project_id
        self.phases: dict[str, dict[str, Any]] = {}
        self.modules: dict[str, dict[str, Any]] = {}

    def add_phase(self, name: str, position: int = 0,
                  status: ProjectStatus = ProjectStatus.PLANNING) -> str:
        phase_id = new_id("phase")
        self.phases[phase_id] = {"phase_id": phase_id, "name": name,
                                 "position": position, "status": status}
        return phase_id

    def add_module(self, name: str, phase_id: str = "",
                   owner_id: str = "") -> str:
        module_id = new_id("module")
        self.modules[module_id] = {"module_id": module_id, "name": name,
                                   "phase_id": phase_id, "owner_id": owner_id,
                                   "tasks": []}
        return module_id

    def set_phase_status(self, phase_id: str,
                         status: ProjectStatus) -> bool:
        phase = self.phases.get(phase_id)
        if phase is None:
            return False
        phase["status"] = status
        return True

    def add_task_to_module(self, module_id: str, task_id: str) -> bool:
        module = self.modules.get(module_id)
        if module is None:
            return False
        module["tasks"].append(task_id)
        return True

    def to_dict(self) -> dict[str, Any]:
        return {"project_id": self.project_id,
                "phases": list(self.phases.values()),
                "modules": list(self.modules.values())}
