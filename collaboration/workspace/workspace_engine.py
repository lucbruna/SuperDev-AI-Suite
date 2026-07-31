"""Workspace engine: ambiente de trabalho colaborativo.

Cria workspaces corporativos com estrutura padrão (Código, Documentação,
Tarefas, IA Agents, Testes, Deploy), settings, permissões e atividade.
"""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_config import CollaborationConfig
from collaboration.collaboration_context import CollaborationContext
from collaboration.collaboration_events import (CollaborationEventType,
                                                CollaborationEvents)
from collaboration.collaboration_logger import get_logger
from collaboration.collaboration_metrics import CollaborationMetrics
from collaboration.collaboration_models import WorkspaceRecord
from collaboration.collaboration_registry import CollaborationRegistry
from collaboration.collaboration_security import CollaborationSecurity
from collaboration.workspace.workspace_manager import WorkspaceManager


class WorkspaceEngine:
    """Orquestrador de workspaces (Fase 2 do Volume 26)."""

    def __init__(self, events: CollaborationEvents | None = None,
                 metrics: CollaborationMetrics | None = None,
                 config: CollaborationConfig | None = None,
                 context: CollaborationContext | None = None,
                 security: CollaborationSecurity | None = None,
                 registry: CollaborationRegistry | None = None,
                 manager: WorkspaceManager | None = None) -> None:
        self._log = get_logger()
        self.events = events or CollaborationEvents()
        self.metrics = metrics or CollaborationMetrics()
        self.config = config or CollaborationConfig()
        self.context = context or CollaborationContext()
        self.security = security or CollaborationSecurity()
        self.manager = manager or WorkspaceManager(registry=registry,
                                                   security=self.security)

    # -- CRUD ---------------------------------------------------------------
    def create(self, name: str, owner_id: str,
               description: str = "", **settings: Any) -> WorkspaceRecord:
        workspace = self.manager.create(name, owner_id, description,
                                        **settings)
        self.metrics.increment("collab.workspaces")
        self.events.publish(CollaborationEventType.WORKSPACE_CREATED,
                            {"workspace_id": workspace.workspace_id,
                             "name": name, "owner_id": owner_id})
        self.manager.activity(workspace.workspace_id).record(
            "workspace.created", owner_id, {"name": name})
        return workspace

    def get(self, workspace_id: str) -> WorkspaceRecord | None:
        return self.manager.get(workspace_id)

    def list(self) -> list[str]:
        return self.manager.list()

    def remove(self, workspace_id: str) -> bool:
        return self.manager.remove(workspace_id)

    def structure(self, workspace_id: str) -> dict[str, Any]:
        return self.manager.structure(workspace_id)

    # -- settings -----------------------------------------------------------
    def get_settings(self, workspace_id: str) -> dict[str, Any]:
        return self.manager.settings(workspace_id).to_dict()

    def update_settings(self, workspace_id: str, **overrides: Any) -> dict[str, Any]:
        settings = self.manager.update_settings(workspace_id, **overrides)
        self.metrics.increment("collab.workspace_updates")
        self.events.publish(CollaborationEventType.WORKSPACE_UPDATED,
                            {"workspace_id": workspace_id})
        return settings.to_dict()

    # -- permissions --------------------------------------------------------
    def can(self, workspace_id: str, role: Any, action: str) -> bool:
        return self.manager.permissions(workspace_id).can(role, action)

    def require(self, workspace_id: str, role: Any, action: str) -> bool:
        return self.manager.permissions(workspace_id).require(role, action)

    # -- activity -----------------------------------------------------------
    def record_activity(self, workspace_id: str, action: str,
                        actor_id: str,
                        details: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.manager.activity(workspace_id).record(action, actor_id,
                                                          details)

    def activity(self, workspace_id: str,
                 limit: int = 50) -> list[dict[str, Any]]:
        return self.manager.activity(workspace_id).list(limit)

    def stats(self) -> dict[str, Any]:
        return {"workspaces": self.manager.count()}
