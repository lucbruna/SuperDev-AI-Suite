"""Project engine: gestão de projetos.

Estrutura corporativa: projeto "Sistema Supermercado ERP" com 12 pessoas
e 8 agentes de IA, fases Planejamento/Desenvolvimento/Testes/Deploy,
módulos (Vendas, Estoque, Financeiro, RH, Relatórios) e progresso.
"""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_config import CollaborationConfig
from collaboration.collaboration_events import (CollaborationEventType,
                                                CollaborationEvents)
from collaboration.collaboration_logger import get_logger
from collaboration.collaboration_metrics import CollaborationMetrics
from collaboration.collaboration_models import ProjectRecord, ProjectStatus
from collaboration.collaboration_registry import CollaborationRegistry
from collaboration.collaboration_security import CollaborationSecurity
from collaboration.projects.project_manager import ProjectManager
from collaboration.projects.project_structure import DEFAULT_PHASES


class ProjectEngine:
    """Orquestrador de projetos (Fase 4 do Volume 26)."""

    def __init__(self, events: CollaborationEvents | None = None,
                 metrics: CollaborationMetrics | None = None,
                 config: CollaborationConfig | None = None,
                 security: CollaborationSecurity | None = None,
                 registry: CollaborationRegistry | None = None,
                 manager: ProjectManager | None = None) -> None:
        self._log = get_logger()
        self.events = events or CollaborationEvents()
        self.metrics = metrics or CollaborationMetrics()
        self.config = config or CollaborationConfig()
        self.security = security or CollaborationSecurity()
        self.manager = manager or ProjectManager(registry=registry)

    def create(self, workspace_id: str, name: str,
               owner_id: str = "", description: str = "",
               status: ProjectStatus = ProjectStatus.PLANNING,
               **settings: Any) -> ProjectRecord:
        project = self.manager.create(workspace_id, name, owner_id,
                                      description, status, **settings)
        structure = self.manager.structure(project.project_id)
        for index, phase in enumerate(DEFAULT_PHASES):
            structure.add_phase(phase, position=index)
        self.metrics.increment("collab.projects")
        self.events.publish(CollaborationEventType.PROJECT_CREATED,
                            {"project_id": project.project_id,
                             "name": name,
                             "workspace_id": workspace_id})
        self.manager.activity(project.project_id).record(
            "project.created", owner_id or workspace_id)
        return project

    def get(self, project_id: str) -> ProjectRecord | None:
        return self.manager.get(project_id)

    def list(self) -> list[str]:
        return self.manager.list()

    def remove(self, project_id: str) -> bool:
        return self.manager.remove(project_id)

    def by_workspace(self, workspace_id: str) -> list[ProjectRecord]:
        return self.manager.by_workspace(workspace_id)

    def update_progress(self, project_id: str,
                        progress: float) -> ProjectRecord | None:
        project = self.manager.update_progress(project_id, progress)
        if project is not None:
            self.metrics.gauge(f"collab.progress.{project_id}", progress)
            self.events.publish(CollaborationEventType.PROJECT_UPDATED,
                                {"project_id": project_id,
                                 "progress": progress})
            self.manager.activity(project_id).record(
                "project.progress", project_id,
                {"progress": progress})
        return project

    def update_status(self, project_id: str,
                      status: ProjectStatus) -> ProjectRecord | None:
        project = self.manager.update_status(project_id, status)
        if project is not None:
            self.events.publish(CollaborationEventType.PROJECT_UPDATED,
                                {"project_id": project_id,
                                 "status": status.value})
            self.manager.activity(project_id).record(
                "project.status", project_id, {"status": status.value})
        return project

    def structure(self, project_id: str) -> dict[str, Any]:
        return self.manager.structure(project_id).to_dict()

    def add_phase(self, project_id: str, name: str,
                  position: int = 0) -> str:
        return self.manager.structure(project_id).add_phase(name, position)

    def add_module(self, project_id: str, name: str,
                   phase_id: str = "", owner_id: str = "") -> str:
        return self.manager.structure(project_id).add_module(
            name, phase_id, owner_id)

    def get_settings(self, project_id: str) -> dict[str, Any]:
        return self.manager.settings(project_id).to_dict()

    def update_settings(self, project_id: str,
                        **overrides: Any) -> dict[str, Any]:
        settings = self.manager.settings(project_id)
        settings.update(**overrides)
        return settings.to_dict()

    def record_activity(self, project_id: str, action: str, actor_id: str,
                        details: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.manager.activity(project_id).record(action, actor_id,
                                                        details)

    def activity(self, project_id: str,
                 limit: int = 100) -> list[dict[str, Any]]:
        return self.manager.activity(project_id).list(limit)

    def metrics_for(self, project_id: str) -> Any:
        return self.manager.metrics(project_id)

    def stats(self) -> dict[str, Any]:
        return {"projects": self.manager.count()}
